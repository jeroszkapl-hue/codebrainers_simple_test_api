import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def get_auth_headers():
    """Log in with the default admin credentials and return a bearer auth header."""
    response = client.post(
        "/api/login", json={"username": "admin", "password": "admin"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_state():
    """Clear in-memory employee store before each test."""
    client.post("/api/employees/reset", headers=get_auth_headers())
    yield


@pytest.fixture
def auth_headers():
    return get_auth_headers()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_success_returns_bearer_token():
    response = client.post(
        "/api/login", json={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 600
    assert body["access_token"]


def test_login_invalid_credentials_rejected():
    response = client.post(
        "/api/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


def test_employees_endpoint_requires_auth():
    response = client.get("/api/employees")
    assert response.status_code == 401


def test_employees_endpoint_rejects_invalid_token():
    response = client.get(
        "/api/employees", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_add_employee_success(auth_headers):
    payload = {
        "name": "Jan Kowalski",
        "salary": 5000,
        "age": 30,
        "position": "Mid QA",
        "on_leave": False,
    }
    response = client.post("/api/employees", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Jan Kowalski"


def test_add_employee_invalid_age_rejected(auth_headers):
    payload = {
        "name": "Jan Kowalski",
        "salary": 5000,
        "age": 17,  # below minimum of 18
        "position": "Mid QA",
        "on_leave": False,
    }
    response = client.post("/api/employees", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_get_employees_returns_added_employee(auth_headers):
    client.post(
        "/api/employees",
        json={
            "name": "Anna Nowak",
            "salary": 6000,
            "age": 28,
            "position": "Senior QA",
            "on_leave": True,
        },
        headers=auth_headers,
    )
    response = client.get("/api/employees", headers=auth_headers)
    assert response.status_code == 200
    employees = response.json()
    assert len(employees) == 1
    assert employees[0]["name"] == "Anna Nowak"


def test_delete_nonexistent_employee_returns_404(auth_headers):
    response = client.delete("/api/employees/999", headers=auth_headers)
    assert response.status_code == 404
