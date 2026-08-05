"""Fixtures shared by tests/integration and tests/functional.

Both suites talk to the app over real HTTP rather than through FastAPI's
in-process ASGI test transport (which is what tests/unit uses), so they
share one live server for the whole session instead of each spinning up
their own.
"""

import os
import socket
import tempfile
import threading
import time

import httpx
import pytest
import uvicorn

# Point the app at an isolated, throwaway SQLite file for the whole test
# session, instead of the real employees.db a developer might have sitting
# next to the app from running `python run.py` locally. Must happen before
# `main` (which imports `db` and resolves DB_PATH at import time) is
# imported anywhere below — including by tests/unit, which imports it
# directly. setdefault() still lets CI or a developer override this
# explicitly.
os.environ.setdefault(
    "DB_PATH",
    os.path.join(tempfile.mkdtemp(prefix="employee-api-tests-"), "test_employees.db"),
)

import main
from main import app


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


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset employees (SQLite, via db.py) and in-memory tokens before and after every test.

    The live server runs in a background thread of this same process, so
    the module-level state in main.py can be reset directly. This also
    runs for tests/unit (harmless there — it already resets state itself
    via the /api/employees/reset endpoint) since it's registered at the
    tests/ root.
    """

    def reset():
        main._reset_storage()
        main.active_tokens.clear()

    reset()
    yield
    reset()
