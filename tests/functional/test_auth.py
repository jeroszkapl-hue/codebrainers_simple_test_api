"""FT-AUTH-xx — login and bearer-token authorization.

See tests/functional/TEST_PLAN.md for the full test case list with steps.
"""


def test_ft_auth_01_login_with_valid_credentials_issues_token(api):
    """FT-AUTH-01: valid admin/admin credentials return a usable bearer token."""
    response = api.post("/api/login", json={"username": "admin", "password": "admin"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 600
    assert body["access_token"]


def test_ft_auth_02_login_with_wrong_password_rejected(api):
    """FT-AUTH-02: correct username with the wrong password is rejected."""
    response = api.post("/api/login", json={"username": "admin", "password": "wrong"})

    assert response.status_code == 401


def test_ft_auth_03_login_with_unknown_username_rejected(api):
    """FT-AUTH-03: an unrecognized username is rejected."""
    response = api.post("/api/login", json={"username": "nobody", "password": "admin"})

    assert response.status_code == 401


def test_ft_auth_04_login_with_missing_fields_returns_validation_error(api):
    """FT-AUTH-04: omitting a required field returns a 422, not a 401/500."""
    response = api.post("/api/login", json={"username": "admin"})

    assert response.status_code == 422


def test_ft_auth_05_protected_endpoint_without_token_rejected(api):
    """FT-AUTH-05: calling a protected endpoint with no Authorization header."""
    response = api.get("/api/employees")

    assert response.status_code == 401


def test_ft_auth_06_protected_endpoint_with_garbage_token_rejected(api):
    """FT-AUTH-06: a well-formed but unissued bearer token is rejected."""
    response = api.get(
        "/api/employees", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


def test_ft_auth_07_logout_invalidates_the_token(api, auth_headers):
    """FT-AUTH-07: a token no longer works against protected endpoints after logout."""
    logout_response = api.post("/api/logout", headers=auth_headers)
    assert logout_response.status_code == 200
    assert logout_response.json() == {"status": "logged_out"}

    response = api.get("/api/employees", headers=auth_headers)
    assert response.status_code == 401


def test_ft_auth_08_logout_without_token_rejected(api):
    """FT-AUTH-08: logout itself requires a valid bearer token."""
    response = api.post("/api/logout")

    assert response.status_code == 401
