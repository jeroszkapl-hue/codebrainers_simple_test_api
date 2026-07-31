"""End-to-end HTTP tests against the live server (see conftest.live_server)."""


def test_health_check_over_real_http(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unauthenticated_request_rejected_over_real_http(client):
    response = client.get("/api/employees")
    assert response.status_code == 401


def test_static_assets_served_over_real_http(client):
    root = client.get("/")
    assert root.status_code == 200
    assert "text/html" in root.headers["content-type"]

    login_page = client.get("/login")
    assert login_page.status_code == 200
    assert "text/html" in login_page.headers["content-type"]

    css = client.get("/static/css/theme.css")
    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]


def test_full_employee_lifecycle(client):
    """Login, create, list, update, delete, and confirm the store is empty again."""
    login = client.post("/api/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/employees",
        json={
            "name": "Jan Kowalski",
            "salary": 5000,
            "age": 30,
            "position": "Mid QA",
            "on_leave": False,
        },
        headers=headers,
    )
    assert created.status_code == 200
    emp_id = created.json()["id"]

    listed = client.get("/api/employees", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/api/employees/{emp_id}",
        json={
            "name": "Jan Kowalski",
            "salary": 5500,
            "age": 30,
            "position": "Senior QA",
            "on_leave": True,
        },
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["salary"] == 5500
    assert updated.json()["position"] == "Senior QA"

    deleted = client.delete(f"/api/employees/{emp_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json() == {"status": "deleted"}

    empty = client.get("/api/employees", headers=headers)
    assert empty.status_code == 200
    assert empty.json() == []


def test_reset_endpoint_clears_employees(client):
    login = client.post("/api/login", json={"username": "admin", "password": "admin"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.post(
        "/api/employees",
        json={
            "name": "Anna Nowak",
            "salary": 6000,
            "age": 28,
            "position": "Senior QA",
            "on_leave": False,
        },
        headers=headers,
    )

    reset = client.post("/api/employees/reset", headers=headers)
    assert reset.status_code == 200
    assert reset.json() == {"status": "reset"}

    listed = client.get("/api/employees", headers=headers)
    assert listed.json() == []
