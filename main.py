import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Dummy Employee API")


# -------------------
# AUTH
# -------------------
TOKEN_TTL_MINUTES = 10
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "admin"

security = HTTPBearer(auto_error=False)

# token -> expiry (UTC)
active_tokens: dict[str, datetime] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def issue_token() -> TokenResponse:
    token = secrets.token_urlsafe(32)
    active_tokens[token] = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)
    return TokenResponse(access_token=token, expires_in=TOKEN_TTL_MINUTES * 60)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    expiry = active_tokens.get(token)

    if expiry is None or datetime.now(timezone.utc) > expiry:
        active_tokens.pop(token, None)
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@app.post("/api/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    if credentials.username != AUTH_USERNAME or credentials.password != AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return issue_token()


# -------------------
# ENUMS
# -------------------
class PositionEnum(str, Enum):
    junior = "Junior QA"
    mid = "Mid QA"
    senior = "Senior QA"
    lead = "QA Lead"


# -------------------
# Models
# -------------------
class Employee(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9]+(?: [A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9]+)*$",
    )

    salary: int = Field(..., ge=1, le=200000)
    age: int = Field(..., ge=18, le=65)

    position: PositionEnum

    on_leave: bool = False

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v):
        if v < 0:
            raise ValueError("Salary below minimum wage threshold")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 18 or v > 65:
            raise ValueError("Age should be between 18 and 65")
        return v


class EmployeeResponse(Employee):
    id: int


# -------------------
# In-memory storage
# -------------------
employees: list[EmployeeResponse] = []
current_id = 1


# -------------------
# API
# -------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/employees", response_model=list[EmployeeResponse])
def get_employees(_: str = Depends(verify_token)):
    return employees


@app.post("/api/employees", response_model=EmployeeResponse)
def add_employee(employee: Employee, _: str = Depends(verify_token)):
    global current_id

    emp = EmployeeResponse(id=current_id, **employee.model_dump())

    employees.append(emp)
    current_id += 1

    return emp


@app.put("/api/employees/{emp_id}", response_model=EmployeeResponse)
def update_employee(emp_id: int, employee: Employee, _: str = Depends(verify_token)):

    for i, emp in enumerate(employees):
        if emp.id == emp_id:
            updated = EmployeeResponse(id=emp_id, **employee.model_dump())

            employees[i] = updated
            return updated

    raise HTTPException(status_code=404, detail="Employee not found")


@app.delete("/api/employees/{emp_id}")
def delete_employee(emp_id: int, _: str = Depends(verify_token)):

    for emp in employees:
        if emp.id == emp_id:
            employees.remove(emp)
            return {"status": "deleted"}

    raise HTTPException(status_code=404, detail="Employee not found")


@app.post("/api/employees/reset")
def reset_employees(_: str = Depends(verify_token)):
    global current_id

    employees.clear()
    current_id = 1

    return {"status": "reset"}


# -------------------
# LOGIN UI
# -------------------
@app.get("/login", response_class=HTMLResponse)
def login_ui():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Login - Employee Manager</title>

<style>

* {
    box-sizing: border-box;
}

/* ---------- THEME VARIABLES ---------- */
body.dark {
    --bg: #0f1115;
    --card: #161a22;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --accent: #ff8c00;
    --danger: #e5533d;
    --input-bg: #0f131b;
    --input-border: #262c3a;
}

body.light {
    --bg: #f5f7fa;
    --card: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --accent: #ff8c00;
    --danger: #dc3545;
    --input-bg: transparent;
    --input-border: rgba(0,0,0,0.15);
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s ease, color 0.3s ease;
}

.login-card {
    position: relative;
    background: var(--card);
    padding: 34px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    width: 340px;
    max-width: 90vw;
}

.theme-toggle {
    position: absolute;
    top: 18px;
    right: 18px;
    background: transparent;
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--text);
    padding: 6px 12px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
    font-size: 12px;
    width: auto;
}

.theme-toggle:hover {
    transform: translateY(-2px);
}

.logo {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: rgba(255, 255, 255, 0.05);
    color: var(--text);
    padding: 6px 14px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    display: inline-block;
    margin-bottom: 22px;
}

.logo span {
    color: var(--accent);
}

h1 {
    font-size: 20px;
    margin: 0 0 20px;
}

label {
    display: block;
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 6px;
}

input {
    width: 100%;
    background: var(--input-bg);
    border: 1px solid var(--input-border);
    color: var(--text);
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 16px;
}

input:focus {
    outline: none;
    border-color: var(--accent);
}

button[type="submit"] {
    width: 100%;
    padding: 12px 18px;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    background: var(--accent);
    color: #1a1a1a;
    transition: 0.2s ease;
}

button[type="submit"]:hover {
    transform: translateY(-2px);
}

.error-box {
    margin-top: 15px;
    padding: 12px;
    border-radius: 10px;
    background: rgba(229, 83, 61, 0.12);
    border: 1px solid var(--danger);
    color: var(--danger);
    display: none;
    font-size: 14px;
}

</style>
</head>

<body class="dark">

<div class="login-card">

    <button type="button" class="theme-toggle" onclick="toggleTheme()">
        🌗 Theme
    </button>

    <div class="logo"><span>&lt;/&gt;</span> EmployeeManager</div>

    <h1>Sign in</h1>

    <form id="loginForm">
        <label for="username">Username</label>
        <input id="username" autocomplete="username" autofocus>

        <label for="password">Password</label>
        <input id="password" type="password" autocomplete="current-password">

        <button type="submit">Sign in</button>
    </form>

    <div id="errorBox" class="error-box"></div>

</div>

<script>

// ---------- THEME ----------
function toggleTheme() {

    const body = document.body;

    const newTheme =
        body.classList.contains('dark')
        ? 'light'
        : 'dark';

    body.className = newTheme;

    localStorage.setItem('theme', newTheme);
}

(function initTheme() {

    const saved = localStorage.getItem('theme');

    if (saved) {
        document.body.className = saved;
    }

})();

function showError(message) {
    const box = document.getElementById('errorBox');
    box.innerText = message;
    box.style.display = 'block';
}

function clearError() {
    const box = document.getElementById('errorBox');
    box.innerText = '';
    box.style.display = 'none';
}

// If already logged in with a valid token, skip the login screen.
(function redirectIfAuthenticated() {
    const expiresAt = Number(localStorage.getItem('token_expires_at') || 0);

    if (localStorage.getItem('token') && Date.now() < expiresAt) {
        window.location.href = '/';
    }
})();

document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    clearError();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    let res;

    try {
        res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
    } catch (err) {
        showError('Unable to reach the server');
        return;
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        showError(error.detail || 'Invalid username or password');
        return;
    }

    const data = await res.json();

    localStorage.setItem('token', data.access_token);
    localStorage.setItem('token_expires_at', Date.now() + data.expires_in * 1000);

    window.location.href = '/';
});

</script>

</body>
</html>
"""


# -------------------
# UI
# -------------------
@app.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Employee Manager</title>

<style>

/* ---------- NAVBAR ---------- */
.navbar {
    height: 64px;
    background: var(--card);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

body.dark .navbar {
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.logo {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: rgba(255, 255, 255, 0.1);
    color: var(--text);
    padding: 6px 14px;
    border-radius: 12px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    display: inline-block;
    transition: all 0.3s ease;
}

body.dark .logo {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 20px rgba(255,255,255,0.05);
}

.logo:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 25px rgba(0,0,0,0.35);
}

.logo span {
    color: var(--accent);
}

/* ---------- THEME VARIABLES ---------- */
body.dark {
    --bg: #0f1115;
    --card: #161a22;
    --table: #1c2230;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --accent: #ff8c00;
    --danger: #e5533d;
}

body.light {
    --bg: #f5f7fa;
    --card: #ffffff;
    --table: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --accent: #ff8c00;
    --danger: #dc3545;
}

/* ---------- BASE ---------- */
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    transition: background 0.3s ease, color 0.3s ease;
}

.container {
    max-width: 1200px;
    margin: auto;
    padding: 40px 30px;
}

/* ---------- TOGGLE ---------- */
.navbar-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.toggle {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--text);
    padding: 8px 14px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
}

.btn-reset {
    color: var(--danger);
    border-color: var(--danger);
}

/* ---------- CARD ---------- */
.card {
    background: var(--card);
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin-bottom: 30px;
}

.card.editing {
    border: 1px solid var(--accent);
}

/* ---------- FORM ---------- */
.form-row {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
}

input,
select {
    flex: 1;
    background: transparent;
    border: 1px solid rgba(0,0,0,0.15);
    color: var(--text);
    padding: 12px;
    border-radius: 10px;
}

body.dark input,
body.dark select {
    border-color: #262c3a;
    background: #0f131b;
}

input::placeholder {
    color: var(--muted);
}

input:focus,
select:focus {
    outline: none;
    border-color: var(--accent);
}

.checkbox-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    min-width: 160px;
}

/* ---------- BUTTONS ---------- */
button {
    padding: 12px 18px;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: 0.2s ease;
}

.btn-add,
.btn-update {
    background: var(--accent);
    color: #1a1a1a;
}

.btn-edit {
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--accent);
}

.btn-delete {
    background: transparent;
    color: var(--danger);
    border: 1px solid var(--danger);
}

button:hover {
    transform: translateY(-2px);
}

/* ---------- TABLE ---------- */
table {
    width: 100%;
    border-collapse: collapse;
    background: var(--table);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

th {
    background: rgba(0,0,0,0.05);
    color: var(--accent);
    padding: 16px;
    text-transform: uppercase;
    font-size: 13px;
}

body.dark th {
    background: #111520;
}

td {
    padding: 14px;
    text-align: center;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

body.dark td {
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

tbody tr:hover {
    background: rgba(255,140,0,0.06);
}

.actions {
    display: flex;
    justify-content: center;
    gap: 10px;
}

/* ---------- FOOTER ---------- */
.footer {
    text-align: center;
    margin-top: 40px;
    padding: 20px 0 10px;
    font-size: 13px;
    color: var(--muted);
}

.footer a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
}

/* ---------- ERROR BOX ---------- */
.error-box {
    margin-top: 15px;
    padding: 12px;
    border-radius: 10px;
    background: rgba(229, 83, 61, 0.12);
    border: 1px solid var(--danger);
    color: var(--danger);
    display: none;
    font-size: 14px;
}

/* ---------- MODAL ---------- */
.modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.modal-overlay.open {
    display: flex;
}

.modal-card {
    background: var(--card);
    padding: 26px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    width: 360px;
    max-width: 90vw;
}

.modal-card h3 {
    margin-top: 0;
}

.modal-card p {
    color: var(--muted);
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.btn-cancel {
    background: transparent;
    color: var(--text);
    border: 1px solid rgba(255,255,255,0.15);
}

.btn-confirm-danger {
    background: var(--danger);
    color: #fff;
}

</style>
</head>

<body class="dark">

<div class="container">

<div class="navbar">
    <div class="logo">
        <span>&lt;/&gt;</span> EmployeeManager
    </div>

    <div class="navbar-actions">
        <button class="toggle btn-reset" onclick="resetData()">
            🗑️ Reset Data
        </button>

        <button class="toggle" onclick="toggleTheme()">
            🌗 Theme
        </button>

        <button class="toggle btn-reset" onclick="logout()">
            🚪 Logout
        </button>
    </div>
</div>

<br>

<div class="card" id="formCard">

    <h3 id="form-title">Add Employee</h3>

    <div class="form-row">

        <input id="name" maxlength="50" placeholder="Name">

        <input id="salary" type="number" placeholder="Salary">

        <input id="age" type="number" placeholder="Age">

        <select id="position">
            <option value="">Select position</option>
            <option value="Junior QA">Junior QA</option>
            <option value="Mid QA">Mid QA</option>
            <option value="Senior QA">Senior QA</option>
            <option value="QA Lead">QA Lead</option>
        </select>

        <label class="checkbox-row">
            <input type="checkbox" id="on_leave">
            On vacation
        </label>

        <button
            id="submitBtn"
            class="btn-add"
            onclick="addEmployee()"
        >
            Add
        </button>

    </div>

    <div id="errorBox" class="error-box"></div>

</div>

<table>

<thead>
<tr>
    <th>ID</th>
    <th>Name</th>
    <th>Salary</th>
    <th>Age</th>
    <th>Position</th>
    <th>Vacation</th>
    <th>Actions</th>
</tr>
</thead>

<tbody id="employees"></tbody>

</table>

</div>

<div class="modal-overlay" id="resetModal">
    <div class="modal-card">
        <h3>Reset Data</h3>
        <p>Are you sure you want to delete all employees? This action cannot be undone.</p>

        <div class="modal-actions">
            <button class="btn-cancel" onclick="hideResetModal()">
                Cancel
            </button>

            <button class="btn-confirm-danger" onclick="confirmReset()">
                Delete All
            </button>
        </div>
    </div>
</div>

<div class="footer">
    © <span id="year"></span>
    <a href="http://www.codebrainers.pl">CodeBrainers</a>
    · v<span id="version"></span>
    · Built: <span id="buildTime"></span>
</div>

<script>

// ---------- AUTH ----------
function getToken() {
    return localStorage.getItem('token');
}

function isTokenValid() {
    const expiresAt = Number(localStorage.getItem('token_expires_at') || 0);
    return Boolean(getToken()) && Date.now() < expiresAt;
}

function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('token_expires_at');
}

function goToLogin() {
    clearToken();
    window.location.href = '/login';
}

function logout() {
    goToLogin();
}

// Redirect to login immediately if there's no valid session.
if (!isTokenValid()) {
    goToLogin();
}

// Wrapper around fetch that attaches the bearer token and redirects to
// the login screen if the server reports the session is no longer valid.
async function apiFetch(url, options = {}) {

    if (!isTokenValid()) {
        goToLogin();
        return Promise.reject(new Error('Not authenticated'));
    }

    const headers = Object.assign({}, options.headers, {
        Authorization: `Bearer ${getToken()}`
    });

    const res = await fetch(url, Object.assign({}, options, { headers }));

    if (res.status === 401) {
        goToLogin();
        return Promise.reject(new Error('Session expired'));
    }

    return res;
}

// ----- META INFO -----
const APP_VERSION = "1.3.0";

document.getElementById('year').innerText = new Date().getFullYear();
document.getElementById('version').innerText = APP_VERSION;

const buildDate = new Date();

document.getElementById('buildTime').innerText =
    buildDate.toISOString().replace('T', ' ').substring(0, 16);

// ---------- THEME ----------
function toggleTheme() {

    const body = document.body;

    const newTheme =
        body.classList.contains('dark')
        ? 'light'
        : 'dark';

    body.className = newTheme;

    localStorage.setItem('theme', newTheme);
}

(function initTheme() {

    const saved = localStorage.getItem('theme');

    if (saved) {
        document.body.className = saved;
    }

})();

// ---------- APP ----------
let editId = null;

const nameInput = document.getElementById('name');
const salaryInput = document.getElementById('salary');
const ageInput = document.getElementById('age');
const positionInput = document.getElementById('position');
const onLeaveInput = document.getElementById('on_leave');

function showError(message) {

    const box = document.getElementById('errorBox');

    box.innerText = message;
    box.style.display = 'block';
}

function clearError() {

    const box = document.getElementById('errorBox');

    box.innerText = '';
    box.style.display = 'none';
}

async function handleApiError(res) {

    const error = await res.json();

    if (Array.isArray(error.detail)) {

        const messages = error.detail
            .map(e => `${e.loc.at(-1)}: ${e.msg}`)
            .join(', ');

        showError(messages);

    } else {

        showError(error.detail || "Unknown error");
    }
}

function getFormData() {

    return {
        name: nameInput.value,
        salary: Number(salaryInput.value),
        age: Number(ageInput.value),
        position: positionInput.value,
        on_leave: onLeaveInput.checked
    };
}

async function loadEmployees() {

    const res = await apiFetch('/api/employees');

    const data = await res.json();

    const tbody = document.getElementById('employees');

    tbody.innerHTML = '';

    data.forEach(e => {

        tbody.innerHTML += `
        <tr>
            <td>${e.id}</td>
            <td>${e.name}</td>
            <td>${e.salary}</td>
            <td>${e.age}</td>
            <td>${e.position}</td>
            <td>${e.on_leave ? '✅' : '❌'}</td>

            <td class="actions">

                <button
                    class="btn-edit"
                    onclick="editEmployee(
                        ${e.id},
                        '${e.name}',
                        ${e.salary},
                        ${e.age},
                        '${e.position}',
                        ${e.on_leave}
                    )"
                >
                    Edit
                </button>

                <button
                    class="btn-delete"
                    onclick="deleteEmployee(${e.id})"
                >
                    Delete
                </button>

            </td>
        </tr>`;
    });
}

function editEmployee(
    id,
    name,
    salary,
    age,
    position,
    on_leave
) {

    editId = id;

    nameInput.value = name;
    salaryInput.value = salary;
    ageInput.value = age;
    positionInput.value = position;
    onLeaveInput.checked = on_leave;

    document.getElementById('form-title').innerText =
        "Edit Employee";

    const btn = document.getElementById('submitBtn');

    btn.innerText = "Update";
    btn.className = "btn-update";
    btn.onclick = updateEmployee;

    document.getElementById('formCard')
        .classList.add('editing');
}

async function addEmployee() {

    clearError();

    const res = await apiFetch('/api/employees', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(getFormData())
    });

    if (!res.ok) {
        await handleApiError(res);
        return;
    }

    resetForm();

    loadEmployees();
}

async function updateEmployee() {

    clearError();

    const res = await apiFetch(`/api/employees/${editId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(getFormData())
    });

    if (!res.ok) {
        await handleApiError(res);
        return;
    }

    resetForm();

    loadEmployees();
}

async function deleteEmployee(id) {

    clearError();

    const res = await apiFetch(`/api/employees/${id}`, {
        method: 'DELETE'
    });

    if (!res.ok) {
        await handleApiError(res);
        return;
    }

    loadEmployees();
}

function resetData() {
    document.getElementById('resetModal').classList.add('open');
}

function hideResetModal() {
    document.getElementById('resetModal').classList.remove('open');
}

async function confirmReset() {

    hideResetModal();

    clearError();

    const res = await apiFetch('/api/employees/reset', {
        method: 'POST'
    });

    if (!res.ok) {
        await handleApiError(res);
        return;
    }

    resetForm();

    loadEmployees();
}

function resetForm() {

    editId = null;

    nameInput.value = '';
    salaryInput.value = '';
    ageInput.value = '';
    positionInput.value = '';
    onLeaveInput.checked = false;

    document.getElementById('form-title').innerText =
        "Add Employee";

    const btn = document.getElementById('submitBtn');

    btn.innerText = "Add";
    btn.className = "btn-add";
    btn.onclick = addEmployee;

    document.getElementById('formCard')
        .classList.remove('editing');
}

loadEmployees();

</script>

</body>
</html>
"""
