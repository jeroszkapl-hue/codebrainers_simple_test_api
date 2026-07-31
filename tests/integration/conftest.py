"""Shared fixtures for integration tests.

Unlike tests/unit, which drive the app in-process through FastAPI's ASGI
test transport, these tests boot the real app on a real TCP socket (via
uvicorn, in a background thread) and talk to it over actual HTTP. That
exercises things the ASGI transport skips: socket binding, real header
parsing, and static file responses served over a live connection.
"""

import socket
import threading
import time

import httpx
import pytest
import uvicorn

from main import active_tokens, app, employees


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """Start the FastAPI app on a real socket for the duration of the session."""
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            httpx.get(f"{base_url}/health", timeout=0.5, trust_env=False)
            break
        except httpx.TransportError:
            time.sleep(0.1)
    else:
        raise RuntimeError("live server did not start in time")

    yield base_url

    server.should_exit = True
    thread.join(timeout=5)


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


@pytest.fixture(autouse=True)
def _reset_state():
    """Clear in-memory employees/tokens before and after every test.

    The live server runs in a background thread of this same process, so
    the module-level state in main.py can be reset directly.
    """
    employees.clear()
    active_tokens.clear()
    yield
    employees.clear()
    active_tokens.clear()
