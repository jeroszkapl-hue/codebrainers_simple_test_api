# Selenium (Browser) Test Plan

Browser-driven UI test cases for the Employee Manager app, exercised with a
real headless Chrome instance via Selenium (see `conftest.py`, `test_*.py`
in this directory). Unlike `tests/functional` (which calls the API
directly with `requests`), these tests click actual buttons and read the
actual DOM, so they also cover the frontend JavaScript in `static/js/`.

Preconditions common to all cases: the app is running and reachable; the
in-memory employee/token store is reset before each test; the browser
starts with a clean session (no `localStorage`).

## Login page (`test_login_ui.py`)

| ID | Title | Steps | Expected result | Automated as |
|---|---|---|---|---|
| SEL-LOGIN-01 | Valid credentials redirect to the main page | 1. Open `/login`. 2. Type `admin` in Username, `admin` in Password. 3. Click "Sign in" | Browser navigates to `/` | `test_sel_login_01_valid_credentials_redirect_to_main_page` |
| SEL-LOGIN-02 | Invalid credentials show an inline error | 1. Open `/login`. 2. Type `admin` / `wrong`. 3. Click "Sign in" | Stays on `/login`; error message becomes visible | `test_sel_login_02_invalid_credentials_show_inline_error` |
| SEL-LOGIN-03 | Main page redirects to login without a session | 1. Open `/` directly with no prior login | Browser redirects to `/login` | `test_sel_login_03_main_page_redirects_to_login_without_session` |
| SEL-LOGIN-04 | Theme toggle persists across a reload | 1. Open `/login`. 2. Click the theme toggle button. 3. Reload the page | `<body>` class after reload matches the toggled theme | `test_sel_login_04_theme_toggle_persists_across_reload` |

## Employee management (`test_employee_management_ui.py`)

All cases start from `logged_in_driver` (already signed in via the real login form).

| ID | Title | Steps | Expected result | Automated as |
|---|---|---|---|---|
| SEL-EMP-01 | Adding an employee shows it in the table | 1. Fill Name/Salary/Age/Position. 2. Click "Add" | A new table row appears containing the employee's name | `test_sel_emp_01_add_employee_appears_in_table` |
| SEL-EMP-02 | Editing an employee updates its row | 1. Add an employee. 2. Click "Edit" on its row. 3. Change Salary. 4. Click "Update" | The row reflects the new salary | `test_sel_emp_02_edit_employee_updates_row` |
| SEL-EMP-03 | Deleting an employee removes its row | 1. Add an employee. 2. Click "Delete" on its row | The table has no rows | `test_sel_emp_03_delete_employee_removes_row` |
| SEL-EMP-04 | Invalid input shows an inline error and adds nothing | 1. Fill the form with `age: 10` (below the 18 minimum). 2. Click "Add" | Error message becomes visible; table has no rows | `test_sel_emp_04_invalid_age_shows_inline_error_and_no_row_added` |
| SEL-EMP-05 | Cancelling the reset modal keeps existing data | 1. Add an employee. 2. Click "Reset Data". 3. In the confirmation modal, click "Cancel" | Modal closes; the row is still present | `test_sel_emp_05_reset_modal_cancel_keeps_data` |
| SEL-EMP-06 | Confirming the reset modal clears the table | 1. Add an employee. 2. Click "Reset Data". 3. In the confirmation modal, click "Delete All" | Table has no rows | `test_sel_emp_06_reset_confirm_clears_table` |
| SEL-EMP-07 | Logout returns to the login page | 1. Click "Logout" | Browser navigates to `/login` | `test_sel_emp_07_logout_returns_to_login_page` |

## Requirements

- A Chrome/Chromium install on `PATH`. Selenium 4's built-in Selenium
  Manager downloads a matching `chromedriver` automatically — no manual
  driver setup needed.
- GitHub Actions `ubuntu-latest` runners ship Chrome preinstalled, so no
  extra CI step should be required; if these tests are added to a CI job,
  confirm Chrome is present on that runner image first.

## Out of scope / covered elsewhere

- Field-level validation rules (boundary values, regex edge cases, enum
  values) are covered exhaustively at the API level in
  `tests/functional/test_employee_validation.py`; SEL-EMP-04 here only
  checks that a validation error surfaces correctly *in the UI*.
- Token expiry is covered in `tests/integration/test_auth_flow.py`.

## Running

```bash
pytest tests/selenium                # this suite only
pytest                                # everything (unit + integration + functional + selenium)
```
