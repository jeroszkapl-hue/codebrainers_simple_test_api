---
name: ruff-autofix
description: Run ruff on a Python project, apply every safe automatic fix, and manually resolve the lint errors ruff can't fix on its own — then re-run ruff (and the test suite) to confirm everything is actually clean. Use this whenever the user pastes a failing `ruff check` output (e.g. from CI logs), mentions specific ruff rule codes (UP017, B008, E501, F401, etc.), asks to fix lint errors, "popraw błędy ruff/lintera", "napraw CI", or wants a Python repo's `ruff check` / `ruff format` step to pass. Also reach for this proactively right after writing or editing Python files in a repo that has a ruff config (`[tool.ruff]` in pyproject.toml, or a `ruff.toml`/`.ruff.toml` file), so lint issues get caught before the user discovers them via a failing CI run.
---

## What this skill does

Ruff reports two very different kinds of problems: ones it can fix mechanically by rewriting syntax (formatting, import order, `pyupgrade`-style modernization), and ones that need someone to actually understand the code and change its structure or behavior (a mutable default argument, a dependency-injection call sitting in a function signature, a function that's grown too complex, a bare `except:`). Running `ruff check --fix` only ever solves the first kind. This skill treats the second kind — the part that requires real judgment — as the important half of the job, not an afterthought.

## Workflow

1. **Find the config.** Look for `pyproject.toml` (a `[tool.ruff]` section) or a standalone `ruff.toml` / `.ruff.toml` in the project root. Note the `target-version` (it determines whether fixes like the `datetime.UTC` alias are even valid for this codebase) and any custom `select` / `ignore` rules. Work with the project's existing conventions, don't fight them.

2. **See the current state before touching anything.** Run:
   ```
   ruff check --output-format=github .
   ```
   (or plain `ruff check .` outside of CI). Actually read every reported error and understand what triggered it — don't just glance at the count.

3. **Apply the free wins.** Run:
   ```
   ruff check --fix .
   ruff format .
   ```
   This clears nearly all `UP*` (pyupgrade), import-sorting, whitespace, and quote-style issues automatically. Immediately re-run `ruff check .` afterward — never assume `--fix` resolved everything; plenty of rules (most of flake8-bugbear, for instance) have no automated fix at all.

4. **Handle everything left by hand.** Whatever still shows up after `--fix` almost always needs real understanding of the code, not another mechanical pass. For each remaining error:
   - Read the surrounding function first, to understand *why* the code is shaped the way it is, before changing anything.
   - Prefer restructuring the code so the underlying concern the rule exists to catch (a real bug it's trying to prevent) is genuinely addressed, rather than reaching for a `# noqa`.
   - Only add `# noqa: RULE123` — with a one-line comment explaining why — when the flagged pattern is truly intentional and the rule just doesn't understand this particular context. That should be the exception, not the default move.
   - Check the reference table below first; the rules that show up most often already have a known-good fix pattern.

5. **Verify nothing broke.** If the project has tests (a `tests/` folder, `pytest` in dependencies, a `[tool.pytest.ini_options]` section), run them after every round of manual fixes. A "lint fix" that silently changes behavior is a regression, not a fix — e.g. changing a mutable default argument changes what the function does across repeated calls, so the test suite is what proves the fix was safe.

6. **Confirm clean, don't just assume it.** Run `ruff check .` one final time, and `ruff format --check .` too if the project's CI checks formatting as a separate step (check for a CI workflow file, e.g. `.github/workflows/*.yml`, to see exactly which commands it runs — match those, not a generic guess). If something genuinely can't be resolved without a decision only the user can make (e.g. bumping the minimum Python version), say so explicitly instead of quietly leaving it unresolved.

7. **Summarize like a human would.** Tell the user what was auto-fixed (usually not worth enumerating line-by-line — "ruff auto-fixed N formatting/import issues" is enough) versus what needed a manual or structural change and *why*. The manual fixes are the part they actually want explained.

## Common non-autofixable rules and how to resolve them

- **B008** — a call like `Depends(...)`, `Query(...)` etc. sitting in a function's default argument. Ruff auto-exempts this for functions decorated as route handlers (e.g. `@app.get(...)`) because that's the standard FastAPI idiom — but it still flags plain dependency-provider functions that aren't themselves routes (e.g. a `verify_token(credentials = Depends(security))` helper used via `Depends(verify_token)` elsewhere). Fix: hoist the call to a module-level singleton and reference the name as the default — `security_dep = Depends(security)`, then `def verify_token(credentials=security_dep):`. Behavior is identical; only the inline call is removed.
- **B006** — a mutable default argument (`def f(x=[])`, `def f(x={})`). Fix: default to `None` and create the mutable value inside the function body instead (`x = [] if x is None else x`).
- **UP017** — `datetime.timezone.utc` instead of the `datetime.UTC` alias. Fix: `from datetime import UTC, datetime, ...` and replace `timezone.utc` with `UTC` everywhere. Only apply this if the project's `target-version` is `py311` or newer (the alias didn't exist before) — check that first, otherwise this "fix" breaks the code on older interpreters actually in use.
- **E722** — bare `except:`. Fix: catch the specific exception type(s) actually expected. If literally anything can happen and must be swallowed, use `except Exception:` and add a comment saying why.
- **C901 / "too complex"** — a function doing too much. Fix: extract cohesive chunks into named helper functions rather than suppressing the warning; this is one of the rare cases where the "real" fix is more valuable than the lint pass itself.
- **F841** — an unused local variable. Fix: usually just delete it. If it's intentionally unused (e.g. part of a tuple unpack), prefix it with `_`.
- **ARG001 / ARG002** — an unused function or method argument. Fix: if it's required by an interface you don't control (overriding a method, a framework callback signature, a FastAPI dependency), prefix with `_` or add a narrowly-scoped `# noqa`; if it's genuinely dead, remove the parameter.

## If ruff isn't installed

Install it before doing anything else rather than trying to hand-emulate its checks: `pip install ruff --break-system-packages` in a sandboxed/system Python, or plain `pip install ruff` inside a project's virtualenv.
