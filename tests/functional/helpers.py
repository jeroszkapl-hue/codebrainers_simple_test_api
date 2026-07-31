"""Shared test data for tests/functional."""

VALID_EMPLOYEE = {
    "name": "Jan Kowalski",
    "salary": 5000,
    "age": 30,
    "position": "Mid QA",
    "on_leave": False,
}


def make_employee(**overrides):
    """Return a valid employee payload with the given fields overridden."""
    payload = dict(VALID_EMPLOYEE)
    payload.update(overrides)
    return payload
