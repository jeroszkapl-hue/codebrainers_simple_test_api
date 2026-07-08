# Changelog

All notable changes to this project are documented in this file.

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
