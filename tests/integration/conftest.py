"""Fixtures specific to tests/integration.

See tests/conftest.py for the shared `live_server` fixture. Unlike
tests/unit, which drives the app in-process through FastAPI's ASGI test
transport, this suite talks to the live server over actual HTTP.
"""

import httpx
import pytest


@pytest.fixture
def client(live_server):
    """An httpx client bound to the live server.

    trust_env=False keeps the client from picking up HTTP_PROXY/NO_PROXY
    (or similar) from the host environment, so these local-loopback
    requests are unaffected by whatever proxy settings a dev machine or CI
    runner happens to have.
    """
    with httpx.Client(base_url=live_server, trust_env=False) as http_client:
        yield http_client
