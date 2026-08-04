# Functional Test Plan

Black-box test cases for the Employee Manager API, exercised over real HTTP
using the `requests` library (see `conftest.py`, `test_*.py` in this
directory). Each case below maps 1:1 to an automated test named in the
"Automated as" column.

Preconditions common to all cases: the app is running and reachable; the
in-memory employee store and token store are reset before each test.

## Authentication (`test_auth.py`)

| ID | Title | Steps | Expected result | Automated as |
|---|---|---|---|---|
| FT-AUTH-01 | Login with valid credentials issues a token | 1. `POST /api/login` with `{"username": "admin", "password": "admin"}` | `200`; body has `token_type: "bearer"`, `expires_in: 600`, non-empty `access_token` | `test_ft_auth_01_login_with_valid_credentials_issues_token` |
| FT-AUTH-02 | Login with wrong password rejected | 1. `POST /api/login` with `{"username": "admin", "password": "wrong"}` | `401` | `test_ft_auth_02_login_with_wrong_password_rejected` |
| FT-AUTH-03 | Login with unknown username rejected | 1. `POST /api/login` with `{"username": "nobody", "password": "admin"}` | `401` | `test_ft_auth_03_login_with_unknown_username_rejected` |
| FT-AUTH-04 | Login with missing field returns validation error | 1. `POST /api/login` with `{"username": "admin"}` (no `password`) | `422` | `test_ft_auth_04_login_with_missing_fields_returns_validation_error` |
| FT-AUTH-05 | Protected endpoint without token rejected | 1. `GET /api/employees` with no `Authorization` header | `401` | `test_ft_auth_05_protected_endpoint_without_token_rejected` |
| FT-AUTH-06 | Protected endpoint with garbage token rejected | 1. `GET /api/employees` with `Authorization: Bearer not-a-real-token` | `401` | `test_ft_auth_06_protected_endpoint_with_garbage_token_rejected` |
| FT-AUTH-07 | Logout invalidates the token | 1. Log in. 2. `POST /api/logout` with the token. 3. `GET /api/employees` with the same (now revoked) token | Step 2: `200`, `{"status": "logged_out"}`. Step 3: `401` | `test_ft_auth_07_logout_invalidates_the_token` |
| FT-AUTH-08 | Logout without token rejected | 1. `POST /api/logout` with no `Authorization` header | `401` | `test_ft_auth_08_logout_without_token_rejected` |

## Health check & static assets (`test_health_and_static.py`)

| ID | Title | Steps | Expected result | Automated as |
|---|---|---|---|---|
| FT-STATIC-01 | Health check reports ok | 1. `GET /health` (no auth) | `200`; body `{"status": "ok"}` | `test_ft_static_01_health_check_reports_ok` |
| FT-STATIC-02 | Root page is served | 1. `GET /` | `200`; `Content-Type` contains `text/html` | `test_ft_static_02_root_page_is_served` |
| FT-STATIC-03 | Login page is served | 1. `GET /login` | `200`; `Content-Type` contains `text/html` | `test_ft_static_03_login_page_is_served` |
| FT-STATIC-04 | Static CSS asset is served | 1. `GET /static/css/theme.css` | `200`; `Content-Type` contains `text/css` | `test_ft_static_04_static_css_asset_is_served` |

## Employee field validation — `POST /api/employees` (`test_employee_validation.py`)

Steps below assume a valid bearer token has already been obtained (`auth_headers` fixture) unless noted otherwise.

| ID | Title | Steps | Expected result | Automated as |
|---|---|---|---|---|
| FT-VAL-01 | Valid employee accepted | 1. Log in. 2. `POST /api/employees` with a fully valid payload (`name`, `salary`, `age`, `position`, `on_leave`) | `200`; response includes `id: 1` and the submitted fields | `test_ft_val_01_valid_employee_is_accepted` |
| FT-VAL-02 | Name accepts Polish diacritics | 1. `POST /api/employees` with `name: "Łukasz Wąż"` | `200`; `name` round-trips unchanged | `test_ft_val_02_name_accepts_polish_diacritics` |
| FT-VAL-03 | Invalid names rejected | 1. `POST /api/employees` with `name` = empty string / 51-char string / `"Jan@Kowalski"` / `"Jan  Kowalski"` (double space) / `"  Jan"` (leading space) — one case per run | `422` in every case | `test_ft_val_03_invalid_names_rejected[...]` (parametrized) |
| FT-VAL-04 | Salary boundaries accepted | 1. `POST /api/employees` with `salary: 1`, then separately `salary: 200000` | `200` in both cases; `salary` echoed back | `test_ft_val_04_salary_boundaries_accepted[...]` |
| FT-VAL-05 | Invalid salary rejected | 1. `POST /api/employees` with `salary` = `0` / `-100` / `200001` / `"not-a-number"` | `422` in every case | `test_ft_val_05_invalid_salary_rejected[...]` |
| FT-VAL-06 | Age boundaries accepted | 1. `POST /api/employees` with `age: 18`, then separately `age: 65` | `200` in both cases; `age` echoed back | `test_ft_val_06_age_boundaries_accepted[...]` |
| FT-VAL-07 | Invalid age rejected | 1. `POST /api/employees` with `age: 17`, then separately `age: 66` | `422` in both cases | `test_ft_val_07_invalid_age_rejected[...]` |
| FT-VAL-08 | Each valid position accepted | 1. `POST /api/employees` once per value of `position`: `"Junior QA"`, `"Mid QA"`, `"Senior QA"`, `"QA Lead"` | `200` each time; `position` echoed back | `test_ft_val_08_each_valid_position_accepted[...]` |
| FT-VAL-09 | Unknown position rejected | 1. `POST /api/employees` with `position: "Intern"` | `422` | `test_ft_val_09_unknown_position_rejected` |
| FT-VAL-10 | Missing position rejected | 1. `POST /api/employees` with the `position` key omitted | `422` | `test_ft_val_10_missing_position_rejected` |
| FT-VAL-11 | `on_leave` defaults to false | 1. `POST /api/employees` with the `on_leave` key omitted | `200`; `on_leave: false` in response | `test_ft_val_11_on_leave_defaults_to_false` |
| FT-VAL-12 | `on_leave: true` is stored | 1. `POST /api/employees` with `on_leave: true` | `200`; `on_leave: true` in response | `test_ft_val_12_on_leave_true_is_stored` |
| FT-VAL-13 | Missing required field rejected | 1. `POST /api/employees` with the `salary` key omitted | `422` | `test_ft_val_13_missing_required_field_rejected` |
| FT-VAL-14 | Unknown extra field ignored | 1. `POST /api/employees` with an extra undocumented key (`department: "QA"`) added to an otherwise valid payload | `200`; `department` is not present in the response body | `test_ft_val_14_unknown_extra_field_is_ignored` |
| FT-VAL-15 | Create without auth rejected | 1. `POST /api/employees` with a valid payload but no `Authorization` header | `401` | `test_ft_val_15_create_without_auth_rejected` |

## Employee CRUD workflow (`test_employee_workflow.py`)

| ID | Title | Steps | Expected result | Automated as |
|---|---|---|---|---|
| FT-WF-01 | Employee list empty after reset | 1. Log in. 2. `GET /api/employees` | `200`; body `[]` | `test_ft_wf_01_employee_list_is_empty_after_reset` |
| FT-WF-02 | Created employee appears in list | 1. Log in. 2. `POST /api/employees` with a valid payload. 3. `GET /api/employees` | `200`; list has 1 item matching the created employee | `test_ft_wf_02_created_employee_appears_in_list` |
| FT-WF-03 | Updating an existing employee changes its fields | 1. Log in. 2. Create an employee. 3. `PUT /api/employees/{id}` with new `salary`, `position`, `on_leave` values | `200`; response reflects the updated fields under the same `id` | `test_ft_wf_03_updating_existing_employee_changes_fields` |
| FT-WF-04 | Updating a non-existent employee returns 404 | 1. Log in. 2. `PUT /api/employees/999999` with a valid payload | `404` | `test_ft_wf_04_updating_nonexistent_employee_returns_404` |
| FT-WF-05 | Deleting an existing employee removes it | 1. Log in. 2. Create an employee. 3. `DELETE /api/employees/{id}`. 4. `GET /api/employees` | Step 3: `200`, `{"status": "deleted"}`. Step 4: `[]` | `test_ft_wf_05_deleting_existing_employee_removes_it` |
| FT-WF-06 | Deleting a non-existent employee returns 404 | 1. Log in. 2. `DELETE /api/employees/999999` | `404` | `test_ft_wf_06_deleting_nonexistent_employee_returns_404` |
| FT-WF-07 | Reset clears employees and restarts the ID counter | 1. Log in. 2. Create two employees (first gets `id: 1`). 3. `POST /api/employees/reset`. 4. `GET /api/employees`. 5. Create another employee | Step 3: `200`, `{"status": "reset"}`. Step 4: `[]`. Step 5: new employee gets `id: 1` again | `test_ft_wf_07_reset_clears_employees_and_restarts_id_counter` |

## Out of scope / covered elsewhere

- **Token expiry** (waiting out or forcing the 10-minute TTL) is exercised in `tests/integration/test_auth_flow.py::test_expired_token_rejected`, which manipulates the in-process token store directly — not reproducible as a pure black-box `requests` test without either waiting 10 real minutes or a TTL override hook.
- **Concurrent request / race-condition behavior** is not covered by either suite.

## Running

```bash
pytest tests/functional            # this suite only
pytest tests/functional -k val     # just the validation cases
pytest                              # everything (unit + integration + functional)
```
