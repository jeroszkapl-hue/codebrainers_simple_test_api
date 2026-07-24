import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    """Clear in-memory employee store before each test."""
    client.post("/api/employees/reset")
    yield


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_employee_success():
    payload = {
        "name": "Jan Kowalski",
        "salary": 5000,
        "age": 30,
        "position": "Mid QA",
        "on_leave": False,
    }
    response = client.post("/api/employees", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Jan Kowalski"


def test_add_employee_invalid_age_rejected():
    payload = {
        "name": "Jan Kowalski",
        "salary": 5000,
        "age": 17,  # below minimum of 18
        "position": "Mid QA",
        "on_leave": False,
    }
    response = client.post("/api/employees", json=payload)
    assert response.status_code == 422


def test_get_employees_returns_added_employee():
    client.post(
        "/api/employees",
        json={
            "name": "Anna Nowak",
            "salary": 6000,
            "age": 28,
            "position": "Senior QA",
            "on_leave": True,
        },
    )
    response = client.get("/api/employees")
    assert response.status_code == 200
    employees = response.json()
    assert len(employees) == 1
    assert employees[0]["name"] == "Anna Nowak"


def test_delete_nonexistent_employee_returns_404():
    response = client.delete("/api/employees/999")
    assert response.status_code == 404
