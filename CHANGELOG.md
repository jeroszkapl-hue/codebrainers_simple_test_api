# Changelog

All notable changes to this project are documented in this file.

## [1.4.0]

### Added
- `POST /api/logout` endpoint — revokes the caller's bearer token server-side (removes it from `active_tokens`), requires a valid token, and returns `{"status": "logged_out"}`. Previously the `Logout` button only cleared `localStorage` client-side; the token itself stayed valid on the server until its 10-minute TTL expired.
- Coverage gate in CI: `pytest --cov=main --cov-report=term-missing` with a 90% floor (`[tool.coverage.report] fail_under` in `pyproject.toml`), scoped to `main.py` since `run.py` (the PyInstaller/uvicorn entrypoint) is covered by the build jobs' smoke tests instead.
- `tests/integration/` — end-to-end tests that boot the real app on a live TCP socket (via `uvicorn`, in a background thread) and exercise it over actual HTTP, covering the full login → create → list → update → delete → reset employee workflow, static asset serving, and token expiry. Complements `tests/unit`, which drives the app in-process through FastAPI's ASGI test transport.
- `tests/functional/` — black-box functional tests built on the `requests` library, covering auth, health/static endpoints, and the full set of `Employee` field validation rules (name pattern, salary/age boundaries, position enum, `on_leave` default) plus the CRUD/reset workflow. Test cases are cataloged with steps in `tests/functional/TEST_PLAN.md`. Shares the live server from `tests/integration` via a new `tests/conftest.py`.
- `httpx2`, `httpcore2`, and `truststore` to `requirements.txt` — `starlette.testclient` now prefers `httpx2` and emits a `StarletteDeprecationWarning` when it falls back to `httpx`; installing `httpx2` silences that warning.
- `requests` (plus `certifi`, `charset-normalizer`, `urllib3`) to `requirements.txt` for `tests/functional`.
- `tests/selenium/` — browser-driven UI tests using Selenium against a real headless Chrome instance, covering the login page (valid/invalid credentials, session-guard redirect, theme persistence) and the main page (add/edit/delete employee, inline validation errors, the reset-data confirmation modal, logout). Cases cataloged with steps in `tests/selenium/TEST_PLAN.md`. Also reuses the shared `live_server` fixture from `tests/conftest.py`.
- `selenium` (plus `trio`, `trio-websocket`, `websocket-client`, `attrs`, `sortedcontainers`, `outcome`, `sniffio`, `wsproto`) to `requirements.txt` for `tests/selenium`.

### Changed
- `logout()` in `static/js/auth.js` now calls `POST /api/logout` (best-effort — a network error doesn't block the local logout) before clearing `localStorage` and redirecting to `/login`.
- The shared test-state reset fixture now also resets `main.current_id` back to `1` between tests, not just the in-memory employee/token stores, so tests that assert on employee IDs aren't order-dependent.
- `requirements.txt` regenerated as a complete, fully-pinned dependency closure (every package actually needed to run the app and the full test suite on the documented Python 3.13/Windows target — including previously-implicit transitive deps like `httpcore`, `iniconfig`, `packaging`, `pluggy`, `Pygments`, `altgraph`, `macholib`, `modulegraph`, `cffi`, and `pycparser`) instead of a partial list that relied on `pip` silently resolving the rest.
- CI's `test` job now runs `pytest --ignore=tests/selenium`, since that suite drives a real headless Chrome browser that the job doesn't provision. `tests/unit`, `tests/integration`, and `tests/functional` are unaffected and still run in CI.
- Extracted the frontend (login screen + main page) out of `main.py`'s embedded HTML/CSS/JS strings into real files under `static/` (`login.html`, `index.html`, `css/theme.css`, `css/login.css`, `css/app.css`, `js/theme.js`, `js/auth.js`, `js/login.js`, `js/app.js`). `main.py` shrank from ~1250 lines to ~230. Theme variables and auth/token helpers are now shared in one place instead of duplicated between pages.
- `main.py` now mounts `/static` via `StaticFiles` and serves `/` and `/login` with `FileResponse`.
- Updated the macOS/Windows PyInstaller build steps in CI to bundle the new `static/` folder (`--add-data`) and to smoke-test `/`, `/login`, and a static asset in addition to `/health`, so a missing frontend asset in a packaged build would be caught automatically.
- Bumped app version to `1.4.0`.

## [1.3.0]

### Added
- `POST /api/login` endpoint — accepts `admin`/`admin` credentials and issues a bearer token valid for 10 minutes.
- Bearer-token authentication required on all `/api/employees*` endpoints (`GET`, `POST`, `PUT`, `DELETE`, `/reset`). Unauthenticated or expired/invalid tokens receive `401 Unauthorized`.
- `/login` page — a standalone login screen matching the app's dark theme; on success it stores the token in `localStorage` and redirects to the main page.
- `Logout` button in the navbar that clears the stored token and returns to the login screen.

### Changed
- Main page now guards itself client-side: it redirects to `/login` if no valid token is present, attaches the bearer token to every API call via a new `apiFetch` helper, and redirects to `/login` automatically if the server responds `401` (e.g. token expired).
- Bumped app version to `1.3.0`.

## [1.2.0]

### Added
- `POST /api/employees/reset` endpoint — deletes all employees and resets the ID counter back to 1.
- `Reset Data` button in the navbar.
- In-app confirmation modal for the reset action (`Cancel` / `Delete All`), replacing the native browser `confirm()` popup. Styled consistently with the app's dark/light theme.

### Changed
- Documented the reset endpoint, navbar button, and confirmation modal in `FUNCTIONAL_REQUIREMENTS.md`, including the rule that all in-app modals must be in English.
- Bumped app version to `1.2.0`.

## [1.1.0]

### Added
- `position` field (dropdown: Junior QA, Mid QA, Senior QA, QA Lead), backed by a `PositionEnum`.
- `on_leave` field (checkbox on the form, ✅/❌ column in the table).
- `FUNCTIONAL_REQUIREMENTS.md` describing the application's functional and UX requirements.
- Postman collection for the API (`.postman/employee_api.json`).
- Clickable CodeBrainers link in the footer.

### Changed
- Desktop launcher (`run.py`) redesigned: branded status window (card layout, logo, accent colors), larger window size.
- Widened the main container layout to accommodate the new form fields.

### Fixed
- Age validation bug where the range check used `and` instead of `or`, allowing invalid ages to pass validation.

### Removed
- Legacy `functional_requirements.docx`, superseded by `FUNCTIONAL_REQUIREMENTS.md`.
