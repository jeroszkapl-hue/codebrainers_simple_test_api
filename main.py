from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Dummy Employee API")

# -------------------
# Data model
# -------------------
class Employee(BaseModel):
    name: str
    salary: int
    age: int


class EmployeeResponse(Employee):
    id: int


# -------------------
# In-memory "database"
# -------------------
employees: List[EmployeeResponse] = []
current_id = 1


# -------------------
# API endpoints
# -------------------
@app.get("/api/employees", response_model=List[EmployeeResponse])
def get_employees():
    return employees


@app.get("/api/employees/{emp_id}", response_model=EmployeeResponse)
def get_employee(emp_id: int):
    for emp in employees:
        if emp.id == emp_id:
            return emp
    raise HTTPException(status_code=404, detail="Employee not found")


@app.post("/api/employees", response_model=EmployeeResponse)
def add_employee(employee: Employee):
    global current_id
    new_emp = EmployeeResponse(id=current_id, **employee.dict())
    employees.append(new_emp)
    current_id += 1
    return new_emp


@app.put("/api/employees/{emp_id}", response_model=EmployeeResponse)
def update_employee(emp_id: int, employee: Employee):
    for idx, emp in enumerate(employees):
        if emp.id == emp_id:
            updated = EmployeeResponse(id=emp_id, **employee.dict())
            employees[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Employee not found")


@app.delete("/api/employees/{emp_id}")
def delete_employee(emp_id: int):
    for emp in employees:
        if emp.id == emp_id:
            employees.remove(emp)
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Employee not found")


# -------------------
# Basic UI
# -------------------
@app.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Manager</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        input { margin: 5px; }
        button { padding: 6px 10px; }
    </style>
</head>
<body>
    <h1>Employee Manager</h1>

    <h3>Add employee</h3>
    <input id="name" placeholder="Name">
    <input id="salary" type="number" placeholder="Salary">
    <input id="age" type="number" placeholder="Age">
    <button onclick="addEmployee()">Add</button>

    <table>
        <thead>
            <tr>
                <th>ID</th><th>Name</th><th>Salary</th><th>Age</th><th>Action</th>
            </tr>
        </thead>
        <tbody id="employees"></tbody>
    </table>

<script>
async function loadEmployees() {
    const res = await fetch('/api/employees');
    const data = await res.json();
    const table = document.getElementById('employees');
    table.innerHTML = '';
    data.forEach(e => {
        table.innerHTML += `
            <tr>
                <td>${e.id}</td>
                <td>${e.name}</td>
                <td>${e.salary}</td>
                <td>${e.age}</td>
                <td><button onclick="deleteEmployee(${e.id})">Delete</button></td>
            </tr>
        `;
    });
}

async function addEmployee() {
    await fetch('/api/employees', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: document.getElementById('name').value,
            salary: Number(document.getElementById('salary').value),
            age: Number(document.getElementById('age').value)
        })
    });
    loadEmployees();
}

async function deleteEmployee(id) {
    await fetch(`/api/employees/${id}`, { method: 'DELETE' });
    loadEmployees();
}

loadEmployees();
</script>
</body>
</html>
"""
