"""Fixtures specific to tests/functional.

Functional tests treat the API purely as a black box: they only assert on
documented request/response contracts (status codes, response bodies,
validation rules) using the `requests` library, the same tool a manual/QA
tester would reach for. See tests/conftest.py for the shared `live_server`
fixture that actually boots the app.
"""

import pytest
import requests


@pytest.fixture
def api(live_server):
    """A requests.Session bound to the live server's base URL.

    trust_env=False stops the session from picking up HTTP_PROXY/NO_PROXY
    from the host environment, so these loopback requests aren't affected
    by whatever proxy settings a dev machine or CI runner happens to have.
    Request paths passed to session methods (e.g. api.get("/health")) are
    resolved against the live server automatically.
    """
    session = requests.Session()
    session.trust_env = False
    original_request = session.request

    def request(method, url, *args, **kwargs):
        return original_request(method, f"{live_server}{url}", *args, **kwargs)

    session.request = request

    with session:
        yield session


@pytest.fixture
def auth_headers(api):
    """Log in with the documented demo credentials and return a bearer header."""
    response = api.post("/api/login", json={"username": "admin", "password": "admin"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
