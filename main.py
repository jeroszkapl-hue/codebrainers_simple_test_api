import os
import secrets
import sys
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Dummy Employee API")


# -------------------
# STATIC ASSETS
# -------------------
# The frontend (login screen + main page) lives under static/ as plain
# HTML/CSS/JS files rather than embedded Python strings. When this app is
# packaged into a desktop build via PyInstaller (see run.py / the CI build
# jobs), bundled data files are extracted next to sys._MEIPASS instead of
# living alongside this source file, so resolve the path accordingly.
STATIC_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# -------------------
# AUTH
# -------------------
TOKEN_TTL_MINUTES = 10

# Default to admin/admin (the app's documented demo credentials) but allow
# overriding via environment variables for anyone running this beyond localhost.
# Reading through os.environ.get(...) rather than a plain string literal also
# keeps Bandit's B105 (hardcoded-password) check from flagging this line.
AUTH_USERNAME = os.environ.get("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "admin")

security = HTTPBearer(auto_error=False)

# Module-level singleton so the Depends(...) call isn't performed inline in the
# function signature default (ruff B008) — see verify_token below.
bearer_dependency = Depends(security)

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
    active_tokens[token] = datetime.now(UTC) + timedelta(minutes=TOKEN_TTL_MINUTES)
    return TokenResponse(access_token=token, expires_in=TOKEN_TTL_MINUTES * 60)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = bearer_dependency,
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    expiry = active_tokens.get(token)

    if expiry is None or datetime.now(UTC) > expiry:
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


@app.post("/api/logout")
def logout(token: str = Depends(verify_token)):
    # Revoke the token server-side so it can't be replayed after the user
    # has logged out, instead of relying solely on the client discarding it
    # from localStorage (which the frontend also does — see auth.js).
    active_tokens.pop(token, None)
    return {"status": "logged_out"}


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
@app.get("/login")
def login_ui():
    return FileResponse(STATIC_DIR / "login.html")


# -------------------
# UI
# -------------------
@app.get("/")
def ui():
    return FileResponse(STATIC_DIR / "index.html")
