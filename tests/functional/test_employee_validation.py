"""FT-VAL-xx — field validation rules for POST /api/employees.

See tests/functional/TEST_PLAN.md for the full test case list with steps.
"""

import pytest

from tests.functional.helpers import make_employee


def test_ft_val_01_valid_employee_is_accepted(api, auth_headers):
    """FT-VAL-01: a fully valid payload is accepted and echoed back with an id."""
    response = api.post("/api/employees", json=make_employee(), headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Jan Kowalski"


def test_ft_val_02_name_accepts_polish_diacritics(api, auth_headers):
    """FT-VAL-02: names with Polish diacritics (ą, ł, ż, ...) are accepted."""
    response = api.post(
        "/api/employees",
        json=make_employee(name="Łukasz Wąż"),
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Łukasz Wąż"


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("", id="empty"),
        pytest.param("A" * 51, id="too-long"),
        pytest.param("Jan@Kowalski", id="invalid-symbol"),
        pytest.param("Jan  Kowalski", id="double-space"),
        pytest.param("  Jan", id="leading-space"),
    ],
)
def test_ft_val_03_invalid_names_rejected(api, auth_headers, name):
    """FT-VAL-03: empty, overlong, or malformed names are rejected with 422."""
    response = api.post(
        "/api/employees", json=make_employee(name=name), headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.parametrize("salary", [1, 200000], ids=["min-boundary", "max-boundary"])
def test_ft_val_04_salary_boundaries_accepted(api, auth_headers, salary):
    """FT-VAL-04: salary is accepted at the documented 1..200000 boundaries."""
    response = api.post(
        "/api/employees", json=make_employee(salary=salary), headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["salary"] == salary


@pytest.mark.parametrize(
    "salary",
    [
        pytest.param(0, id="zero"),
        pytest.param(-100, id="negative"),
        pytest.param(200001, id="over-max"),
        pytest.param("not-a-number", id="wrong-type"),
    ],
)
def test_ft_val_05_invalid_salary_rejected(api, auth_headers, salary):
    """FT-VAL-05: salary outside 1..200000, or of the wrong type, is rejected."""
    response = api.post(
        "/api/employees", json=make_employee(salary=salary), headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.parametrize("age", [18, 65], ids=["min-boundary", "max-boundary"])
def test_ft_val_06_age_boundaries_accepted(api, auth_headers, age):
    """FT-VAL-06: age is accepted at the documented 18..65 boundaries."""
    response = api.post(
        "/api/employees", json=make_employee(age=age), headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["age"] == age


@pytest.mark.parametrize(
    "age",
    [pytest.param(17, id="under-min"), pytest.param(66, id="over-max")],
)
def test_ft_val_07_invalid_age_rejected(api, auth_headers, age):
    """FT-VAL-07: age outside 18..65 is rejected."""
    response = api.post(
        "/api/employees", json=make_employee(age=age), headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.parametrize("position", ["Junior QA", "Mid QA", "Senior QA", "QA Lead"])
def test_ft_val_08_each_valid_position_accepted(api, auth_headers, position):
    """FT-VAL-08: every documented position enum value is accepted."""
    response = api.post(
        "/api/employees", json=make_employee(position=position), headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["position"] == position


def test_ft_val_09_unknown_position_rejected(api, auth_headers):
    """FT-VAL-09: a position outside the enum is rejected."""
    response = api.post(
        "/api/employees", json=make_employee(position="Intern"), headers=auth_headers
    )

    assert response.status_code == 422


def test_ft_val_10_missing_position_rejected(api, auth_headers):
    """FT-VAL-10: position is required and rejected when absent."""
    payload = make_employee()
    del payload["position"]

    response = api.post("/api/employees", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_ft_val_11_on_leave_defaults_to_false(api, auth_headers):
    """FT-VAL-11: omitting on_leave defaults it to false."""
    payload = make_employee()
    del payload["on_leave"]

    response = api.post("/api/employees", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["on_leave"] is False


def test_ft_val_12_on_leave_true_is_stored(api, auth_headers):
    """FT-VAL-12: on_leave=true round-trips correctly."""
    response = api.post(
        "/api/employees", json=make_employee(on_leave=True), headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["on_leave"] is True


def test_ft_val_13_missing_required_field_rejected(api, auth_headers):
    """FT-VAL-13: dropping a required field (salary) is rejected."""
    payload = make_employee()
    del payload["salary"]

    response = api.post("/api/employees", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_ft_val_14_unknown_extra_field_is_ignored(api, auth_headers):
    """FT-VAL-14: an undocumented extra field doesn't break the request."""
    payload = make_employee(department="QA")

    response = api.post("/api/employees", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert "department" not in response.json()


def test_ft_val_15_create_without_auth_rejected(api):
    """FT-VAL-15: creating an employee without a bearer token is rejected."""
    response = api.post("/api/employees", json=make_employee())

    assert response.status_code == 401
