"""Integration tests for the login/token flow over real HTTP."""

from datetime import UTC, datetime, timedelta

from main import active_tokens


def test_login_then_use_token_over_real_http(client):
    login = client.post("/api/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    response = client.get(
        "/api/employees", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_invalid_credentials_rejected_over_real_http(client):
    response = client.post(
        "/api/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


def test_expired_token_rejected(client):
    login = client.post("/api/login", json={"username": "admin", "password": "admin"})
    token = login.json()["access_token"]

    # The live server runs in this same process, so we can force the token
    # to expire without waiting out the real 10-minute TTL.
    active_tokens[token] = datetime.now(UTC) - timedelta(seconds=1)

    response = client.get(
        "/api/employees", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_malformed_bearer_token_rejected(client):
    response = client.get(
        "/api/employees", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_logout_removes_token_from_server_side_store(client):
    login = client.post("/api/login", json={"username": "admin", "password": "admin"})
    token = login.json()["access_token"]
    assert token in active_tokens

    response = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"status": "logged_out"}

    # Not just "the API says 401 now" — the token is actually gone from the
    # in-memory store, not merely expired or shadowed.
    assert token not in active_tokens
