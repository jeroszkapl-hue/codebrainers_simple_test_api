from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from typing import List
from enum import Enum

app = FastAPI(title="Dummy Employee API")


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
        pattern=r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9]+(?: [A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9]+)*$"
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
employees: List[EmployeeResponse] = []
current_id = 1


# -------------------
# API
# -------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/employees", response_model=List[EmployeeResponse])
def get_employees():
    return employees


@app.post("/api/employees", response_model=EmployeeResponse)
def add_employee(employee: Employee):
    global current_id

    emp = EmployeeResponse(
        id=current_id,
        **employee.model_dump()
    )

    employees.append(emp)
    current_id += 1

    return emp


@app.put("/api/employees/{emp_id}", response_model=EmployeeResponse)
def update_employee(emp_id: int, employee: Employee):

    for i, emp in enumerate(employees):
        if emp.id == emp_id:

            updated = EmployeeResponse(
                id=emp_id,
                **employee.model_dump()
            )

            employees[i] = updated
            return updated

    raise HTTPException(status_code=404, detail="Employee not found")


@app.delete("/api/employees/{emp_id}")
def delete_employee(emp_id: int):

    for emp in employees:
        if emp.id == emp_id:
            employees.remove(emp)
            return {"status": "deleted"}

    raise HTTPException(status_code=404, detail="Employee not found")


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
.toggle {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--text);
    padding: 8px 14px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
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

</style>
</head>

<body class="dark">

<div class="container">

<div class="navbar">
    <div class="logo">
        <span>&lt;/&gt;</span> EmployeeManager
    </div>

    <button class="toggle" onclick="toggleTheme()">
        🌗 Theme
    </button>
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

<div class="footer">
    © <span id="year"></span>
    <a href="http://www.codebrainers.pl">CodeBrainers</a>
    · v<span id="version"></span>
    · Built: <span id="buildTime"></span>
</div>

<script>

// ----- META INFO -----
const APP_VERSION = "1.1.0";

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

    const res = await fetch('/api/employees');

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

    const res = await fetch('/api/employees', {
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

    const res = await fetch(`/api/employees/${editId}`, {
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

    const res = await fetch(`/api/employees/${id}`, {
        method: 'DELETE'
    });

    if (!res.ok) {
        await handleApiError(res);
        return;
    }

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