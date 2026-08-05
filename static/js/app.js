// Main Employee Manager page logic. Depends on the shared helpers in
// auth.js (isTokenValid, goToLogin, apiFetch) and theme.js, which must be
// loaded first.

// Redirect to login immediately if there's no valid session.
if (!isTokenValid()) {
    goToLogin();
}

// ----- META INFO -----
const APP_VERSION = "1.5.0";

document.getElementById('year').innerText = new Date().getFullYear();
document.getElementById('version').innerText = APP_VERSION;

const buildDate = new Date();

document.getElementById('buildTime').innerText =
    buildDate.toISOString().replace('T', ' ').substring(0, 16);

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
