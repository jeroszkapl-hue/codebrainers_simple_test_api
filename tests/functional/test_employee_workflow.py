"""FT-WF-xx — end-to-end employee CRUD workflow.

See tests/functional/TEST_PLAN.md for the full test case list with steps.
"""

from tests.functional.helpers import make_employee


def test_ft_wf_01_employee_list_is_empty_after_reset(api, auth_headers):
    """FT-WF-01: a freshly reset store returns an empty list."""
    response = api.get("/api/employees", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_ft_wf_02_created_employee_appears_in_list(api, auth_headers):
    """FT-WF-02: an employee created via POST shows up in a subsequent GET."""
    api.post(
        "/api/employees",
        json=make_employee(name="Anna Nowak"),
        headers=auth_headers,
    )

    response = api.get("/api/employees", headers=auth_headers)

    assert response.status_code == 200
    employees = response.json()
    assert len(employees) == 1
    assert employees[0]["name"] == "Anna Nowak"


def test_ft_wf_03_updating_existing_employee_changes_fields(api, auth_headers):
    """FT-WF-03: PUT on an existing id updates its fields and returns them."""
    created = api.post(
        "/api/employees", json=make_employee(), headers=auth_headers
    ).json()

    response = api.put(
        f"/api/employees/{created['id']}",
        json=make_employee(salary=7000, position="Senior QA", on_leave=True),
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["salary"] == 7000
    assert body["position"] == "Senior QA"
    assert body["on_leave"] is True


def test_ft_wf_04_updating_nonexistent_employee_returns_404(api, auth_headers):
    """FT-WF-04: PUT on an id that doesn't exist returns 404."""
    response = api.put(
        "/api/employees/999999", json=make_employee(), headers=auth_headers
    )

    assert response.status_code == 404


def test_ft_wf_05_deleting_existing_employee_removes_it(api, auth_headers):
    """FT-WF-05: DELETE removes the employee and it no longer appears in GET."""
    created = api.post(
        "/api/employees", json=make_employee(), headers=auth_headers
    ).json()

    response = api.delete(f"/api/employees/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}

    listed = api.get("/api/employees", headers=auth_headers)
    assert listed.json() == []


def test_ft_wf_06_deleting_nonexistent_employee_returns_404(api, auth_headers):
    """FT-WF-06: DELETE on an id that doesn't exist returns 404."""
    response = api.delete("/api/employees/999999", headers=auth_headers)

    assert response.status_code == 404


def test_ft_wf_07_reset_clears_employees_and_restarts_id_counter(api, auth_headers):
    """FT-WF-07: reset empties the store and the next created employee gets id 1."""
    first = api.post(
        "/api/employees", json=make_employee(), headers=auth_headers
    ).json()
    api.post(
        "/api/employees", json=make_employee(name="Anna Nowak"), headers=auth_headers
    )
    assert first["id"] == 1

    reset = api.post("/api/employees/reset", headers=auth_headers)
    assert reset.status_code == 200
    assert reset.json() == {"status": "reset"}

    listed = api.get("/api/employees", headers=auth_headers)
    assert listed.json() == []

    recreated = api.post(
        "/api/employees", json=make_employee(), headers=auth_headers
    ).json()
    assert recreated["id"] == 1
