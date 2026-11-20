# Implementation Report: SCRUM-101 Add a New Employee

Date: 2026-11-20. Branch: `feature/doc-sync-claude` (checked; no commit, push or branch change was made).
Inputs read: `docs/requirements.md`, `docs/architecture.md` (Revision 3), `docs/design-review.md`, `docs/impl-plan.md`, `CLAUDE.md`, `.claude/rules/rule-implementation.md`, the `implementation` skill. Approved requirements, architecture, design review, plan and `docs/sdlc-state.md` were not modified. Unknown = `Not Found`.

## 1. Test evidence (actual runs)

Environment: Python 3.11.9, `.venv` of the repository. Installed into it: Flask 3.1.3, Flask-Login 0.6.3, Flask-WTF 1.3.0 (WTForms 3.3.2), SQLAlchemy 2.0.58, Werkzeug 3.1.9, Click 8.5.1, pytest 9.2.0.

| Command (from repository root) | Result |
|---|---|
| `.venv/Scripts/python -m pytest` (final full run) | 436 passed, 0 failed, 0 skipped, 41.11 s |
| `.venv/Scripts/python -m pytest --collect-only -q` | 436 tests collected |
| `pytest -q tests/test_lockout_concurrency.py tests/test_duplicate_race.py tests/test_unlock_integration.py` repeated 5 times | 13 passed each time (flakiness check of the concurrency and race tests; 5 runs is a small sample) |
| AST check of every function in `src/employee_app/` for type hints | all signatures annotated |

Not run: manual browser check (TASK-046), vulnerability scan (`pip-audit` was not run; plan says vulnerability scanning is `Not Found`), any run on a network file system or on a deployment target.

## 2. Task status

Completed (code and tests exist, listed tests pass):
TASK-002, 003, 004, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014, 015, 016, 017, 018, 019, 020, 021, 022, 023, 024, 025, 026, 027, 028, 029, 030, 031, 032, 033, 034, 035, 036, 037, 038, 039, 040, 042, 043, 047.
TASK-001: resolved by the user before this step (app package `src/employee_app/`, tests in top-level `tests/`); applied, nothing to implement.

Partial:
- TASK-042 notes written (`docs/ops-notes.md`); the final journal-mode choice and file-account setup remain `Not Found` (depends on OQ-A3), as the plan states.
- TASK-044: only the configurable, empty-by-default department list is implemented (config key `departments`, web app refuses an empty list outside `testing`). Real names `Not Found`.
- TASK-048: the full suite was run (section 1), but the traceability check of every FR/NFR/AC id and the final `git status` review for the release gate are for the orchestrator/verifier; remaining blockers are listed in section 7.

Not done:
- TASK-041 (blocked, orchestrator handles the amendment). Note for the request: every id it lists is already referenced by tests, by name or docstring: FR-18, AC-16, AC-17, P-14, P-15 in `tests/test_cmd_unlock_user.py` and `tests/test_unlock_integration.py`; N-20 in `tests/test_unlock_integration.py` (`test_c_...`); E-18 in `tests/test_cmd_unlock_user.py` and `tests/test_unlock_integration.py`. The automated "traceability check" script of TASK-041 was not written.
- TASK-044 real names, TASK-045 (blocked, deployment target `Not Found`).
- TASK-046 (manual browser smoke on four browsers): not performed; no result is claimed.

## 3. TASK-003 and TASK-004 outcomes (library behaviour, actually run)

Confirmed, no contradiction of the architecture found:
- 003a: with `WTF_CSRF_CHECK_DEFAULT=False` the automatic check is off and `csrf.protect()` can be called manually (403 through our handler). Negative control: with the default on, an unauthenticated POST without a token gets 400 (why D-5 is needed).
- 003b: a before-request style authentication check returns 401 before the CSRF check; the request body stream was not read for an unauthenticated request (spy stream, 0 reads). Authenticated without token: 403. Public `POST /login` without token: 403.
- 003c: `WTF_CSRF_TIME_LIMIT=None` keeps a token valid 9 h later (patched time); an integer limit of 3600 expires it. The library default is 3600, not the session lifetime, so the app sets it explicitly (`csrf_lifetime_seconds`, default equal to the 8 h session lifetime). Limit of this check: token age is measured by `time.time`, not by the C-8 clock.
- 003d: `login_user(..., remember=False)` sets no `remember_token` cookie.
- 003e: session cookie has HttpOnly and SameSite=Lax; `Secure` follows `SESSION_COOKIE_SECURE`.
- Additional finding (not in the architecture): over HTTPS (as the app sees the request) Flask-WTF also requires a same-origin `Referer` header on POST (`WTF_CSRF_SSL_STRICT`, default on); without it the POST gets 403. Recorded in `docs/ops-notes.md` section 6 for the deployment target. No code change made.
- 004a: `hide_parameters=True` keeps statement values out of exception text (control without it shows them).
- 004b: `BEGIN IMMEDIATE` waits for the busy timeout at the beginning and then fails at the beginning; a waiting writer succeeds if the holder finishes in time; a deferred read-then-write transaction can fail late under contention (control).
- 004c: an `UPDATE` that matches no row still takes the writer lock (NR-12): it blocks another writer until the transaction ends. This supports the NR-12 decision to skip the lockout write while a lock is active.
- 004d: WAL is active; a reader works while a writer holds an open write transaction. 004e: `PRAGMA foreign_keys=ON` enforces foreign keys. 004f: a unique-index integrity error is distinguishable by re-query after rollback.

## 4. Files

Created (all new):
- `src/employee_app/`: `__init__.py`, `clock.py`, `config.py`, `logging_setup.py`, `security.py`, `extensions.py`, `app.py`; `validation/` (`__init__`, `limits`, `messages`, `text`, `email`, `phone`, `date_dept`, `password`, `employee`, `username`); `db/` (`__init__`, `models`, `errors`, `engine`, `statements`, `verify`, `users`, `lockout`, `employees`); `commands/` (`__init__`, `__main__`, `context`, `accounts`, `cli`); `auth/` (`__init__`, `session`, `loader`, `guard`, `login`); `routes/` (`__init__`, `auth_routes`, `employee_routes`, `errors`); `services/` (`__init__`, `employee`); `templates/` (`base`, `login`, `error`, `employee_form`); `static/` (`style.css`, `form.js`).
- `tests/`: `__init__`, `conftest`, `helpers`, `cmd_helpers`, `web_helpers`, `test_scaffold`, `test_lib_csrf_session`, `test_lib_sqlite`, `test_config`, `test_logging`, `test_validation_{text,email,phone,date_dept,employee}`, `test_db_{schema,lockout,employee_write}`, `test_commands_context`, `test_cmd_{create_user,deactivate_user,unlock_user,logging}`, `test_app_startup`, `test_errors_headers`, `test_auth_{session,csrf,integration}`, `test_login`, `test_login_lockout`, `test_logout`, `test_employee_{service,routes}`, `test_templates`, `test_lockout_{concurrency,fail_closed}`, `test_duplicate_race`, `test_atomicity`, `test_e2e_add_employee`, `test_security`, `test_account_scenarios`, `test_unlock_integration`, `test_perf_smoke`.
- `docs/ops-notes.md` (TASK-042).

Changed existing files (minimal; each reported):
1. `requirements.txt`: appended pinned `Flask==3.1.3`, `Flask-Login==0.6.3`, `Flask-WTF==1.3.0`, `SQLAlchemy==2.0.58`, `Werkzeug==3.1.9` (existing `pytest>=8.0`, `pip-audit>=2.7` lines untouched).
2. `pytest.ini`: added a `markers` entry registering `informative` (used by TASK-047). `pythonpath = src` and `testpaths = tests` unchanged, so the legacy layout is unaffected.
3. `.gitignore`: added `*.db`, `*.sqlite`, `*.sqlite3`, `*.db-wal`, `*.db-shm`, `*.sqlite-wal`, `*.sqlite-shm`, `*-wal`, `*-shm`, `.env.*`, `!.env.example`. (My first append glued onto the unterminated `.venv/` line; found by `git status` and fixed. Final content verified; `git check-ignore` confirms `x.sqlite3`, `x.db-wal`, `.env` are ignored.)
4. Not changed in the original Step 5 pass (later changed by the review fixes, see section 8): `pyproject.toml` (no dependency or script entry added; `packages.find where=["src"]` already discovers `employee_app`), `README.md`, `CHANGELOG.md` (left for the PR step; no edit was necessary to keep legacy working).

Legacy `src/doc_sync/`: in this working tree it is an empty untracked directory and `tests/` was empty before this step (`git ls-files src tests` listed nothing), so there was no legacy code or test to run, modify or delete. Nothing was touched there. Whether legacy `doc_sync` still works: `Not Found` (no legacy code is present to check).

## 5. Design notes and deviations

Deviations from the architecture or plan (all small, none changes an approved behaviour):
1. D-19 "one scoped session per request": implemented as short-lived sessions per operation, always closed with uncommitted work rolled back (`session_scope`). Reason: a session held open across the request would keep a read transaction that can block the writer on SQLite; the pre-check must end before the write (D-25). Test: `test_session_closed_and_uncommitted_work_rolled_back`.
2. TASK-034: for the "lock read fails" injection the account cannot be read, so the user id is unknown; the error log carries the category only (no user id). The failure-path and success-path injections log user id and category.
3. Lockout log event `account_locked` is derived from the count read before the update; under concurrency it can be missed or repeated. The database state (single conditional update) is authoritative; no test depends on this event under concurrency.
4. Conditional-update helpers each commit in their own `BEGIN IMMEDIATE` transaction; the busy wait is both the `sqlite3` timeout and the configured 2 s default.
5. Flask-Login `session_protection` left at its default ("basic"); not discussed in the architecture.
6. A failed `increment_auth_version` during logout surfaces as the generic 500 page and leaves the session in place (visible failure; not specified).
7. Environment variable names and the settings-file format are Proposals (TASK-006 says so): `EMPLOYEE_APP_DB_PATH`, `EMPLOYEE_APP_SECRET_KEY`, `EMPLOYEE_APP_COOKIE_SECURE`, `EMPLOYEE_APP_ENV`, `EMPLOYEE_APP_SETTINGS_FILE`.
8. The `FLASK_DEBUG` environment variable and an app config `DEBUG` override are both treated as a debug request and refused outside development.

Implemented as specified, worth stating: login always verifies a hash (dummy hash for unknown users); NR-12 (no write statement is issued for an already-locked account) is demonstrated by a statement-capturing test; 401 has no `WWW-Authenticate`; `next` is ignored; CSRF token lifetime equals the session lifetime; secrets only from environment; no log field can carry a username, password, hash, cookie, token or employee value (allow-listed fields, enforced in `logging_setup.format_event`); passwords come only from the hidden prompt (test asserts an environment variable is ignored and `--password` is not an option). Test passwords and signing keys are generated with `secrets` or obviously fake constants.

## 6. Tests added (436)

By area: library characterization (TASK-003: 12, TASK-004: 10); clock, config, logging; five validation modules; persistence schema, verification, lockout, employee write; command context and the four commands plus command logging; app startup, headers and errors, session, CSRF, login, lockout, logout; service, routes, templates; mandatory concurrency (`test_lockout_concurrency.py`, includes a deterministic forced-interleaving test), fail-closed (`test_lockout_fail_closed.py`, three injection points), duplicate race (`test_duplicate_race.py`, asserts loser sees email-in-use), atomicity, authentication integration, end-to-end AC-01 to AC-10, security, account scenarios AC-11 to AC-15, unlock integration (a) to (d), informative performance smoke (marker `informative`).

## 7. Incomplete work, blockers and open decisions for the user

- TASK-041: architecture amendment request (NR-13) is with the orchestrator; test references listed in section 2.
- TASK-044 / DEC-3: real department names `Not Found`. Until supplied, the production web app refuses to start (empty list); tests use "Test Dept A" and "Test Dept B".
- TASK-045 / DEC-4 / OQ-A3: deployment target, production WSGI server, HTTPS termination, final journal mode, file-account setup `Not Found`. Also verify the strict Referer behaviour (section 3) on that target.
- TASK-046: manual four-browser check to be done by a person and recorded in verification.
- Operator console script: no `[project.scripts]` entry was added to `pyproject.toml` (not in the plan); commands run as `python -m employee_app.commands <command>`. Decision for the user if a console script is wanted.
- README and CHANGELOG do not yet mention the web app, the operator commands or the settings; left untouched on purpose (minimal change). Needs a decision on who updates them (PR step).
- Residual items from the plan stay `Not Found`: allowed characters, roles other than HR Administrator, audit retention/viewing, password reset and reactivation, written approval record (DEC-5), vulnerability scanning.
- Limits of the evidence: concurrency tests use threads with separate connections on a local file database on this Windows machine; behaviour on other platforms or file systems is not tested.

## 8. Review fixes (after docs/code-review.md, APPROVED_WITH_CONDITIONS)

Changed files: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` (new), `README.md`, `.gitignore` (added `*.egg-info/`), `src/employee_app/app.py`, `tests/test_app_startup.py`, `tests/test_config.py` (test signing key lengthened to 40+ characters). `CHANGELOG.md`, `docs/sdlc-state.md`, `docs/code-review.md` and approved documents untouched.

- REVIEW-001/002: `pyproject.toml` now names the project `employee_app`, finds only `employee_app*` under `src/`, includes templates and static files, declares runtime dependencies `Flask==3.1.3`, `Flask-Login==0.6.3`, `Flask-WTF==1.3.0`, `SQLAlchemy==2.0.58`, `Werkzeug==3.1.9`, `click==8.5.1`, and has the script `employee-admin = employee_app.commands.cli:cli`. The stale `doc_sync` script is removed. Verified: `pip install -e .` into the venv succeeded; from a clean directory with PYTHONPATH unset, `employee-admin --help` listed the four commands, `init-db` worked, `unlock-user ops1` exited 0 and `unlock-user nobody` exited 1 with "Unknown username". Also verified: `flask --app employee_app.app:create_app routes` listed the 5 routes, and the dev server answered `/login` 200 and `/employees/new` 302 (with a generated key and a one-department settings file).
- Finding while verifying: `create-user` could not be driven by piped stdin (the hidden prompt waits for a console on Windows and hung until the timeout). It is for interactive use, as designed; I created the verification user through `create_account` in Python instead. README says "interactive terminal only".
- README: added "Run and install" section (install, variable names only, init-db, create-user, other commands, dev server, tests, dev requirements, pip-audit command); step 1 of the pipeline text now points to `requirements-dev.txt`.
- REVIEW-003: `requirements.txt` holds only runtime pins (plus `click==8.5.1`); `requirements-dev.txt` has `-r requirements.txt`, `pytest==9.2.0`, `pip-audit==2.10.1` (versions installed in the venv). `pip-audit -r requirements.txt` ran and printed "No known vulnerabilities found" (it also printed a venv redirect warning about a temp path).
- REVIEW-004: `check_settings` in `app.py` raises `StartupError` ("Setting EMPLOYEE_APP_SECRET_KEY is too short (minimum 32 characters)", never the value) for keys under 32 characters. New parametrised test covers 0, 31 (rejected), 32, 33, 64 (accepted). Existing fixtures already used keys of 34+ characters except `tests/test_config.py` (31 characters, lengthened).
- Full suite after the fixes: `.venv/Scripts/python -m pytest` gave 441 passed, 0 failed (436 before plus 5 new cases).
- Not done / not changed: REVIEW-005 to 009 accepted as-is; no production server chosen; CHANGELOG not edited as instructed.
