> **CURRENT VERDICT (after re-review, section 8): APPROVED_WITH_CONDITIONS.** REVIEW-001 to REVIEW-004 are resolved or partially resolved with evidence; REVIEW-005 to REVIEW-009 were accepted by the user. Sections 1 to 7 below are the original review (verdict at that time: APPROVED_WITH_CONDITIONS).

# Code Review: SCRUM-101 Add a New Employee (Step 6)

Reviewer: independent code reviewer (Step 6). Branch `feature/doc-sync-claude`, HEAD "docs: record pipeline state through step 5".
Scope: `src/employee_app/` (48 tracked files), `tests/`, `requirements.txt`, `pyproject.toml`, `pytest.ini`, `.gitignore`, `docs/ops-notes.md`.
Note: the stage command names `docs/architecture-design.md` and `src/doc_sync/`; the real inputs are `docs/architecture.md` (Revision 3) and `src/employee_app/` (`src/doc_sync/` does not exist in the tree). No source or test file was modified by this review. Unknown = `Not Found`.

## 1. Review summary

Verdict: **APPROVED_WITH_CONDITIONS**. No Critical, High or confirmed functional defect was found. The implementation matches the approved architecture and the design-review conditions that were checked (section 5). None of the findings blocks verification; the Medium item is an operability/documentation gap that should be fixed or explicitly accepted.

Findings by severity: Critical 0, High 0, Medium 1 (REVIEW-001), Low 5 (REVIEW-002 to 006), Informational 3 (REVIEW-007 to 009). Total 9.

## 2. Evidence actually gathered

| Check | Command / method | Result |
|---|---|---|
| Full test suite | `.venv/Scripts/python -m pytest -q` | 436 passed in 41.45 s (matches the report) |
| Stray files after tests | `git status --short` before and after | Clean both times; no untracked db or other files |
| Type hints | AST walk over every function in `src/employee_app/` | 0 unannotated signatures (report claim confirmed) |
| Secrets / prints / log calls | grep for `print(`, `logging.*`, `getenv`, `os.environ`, literal password/secret/token assignments in `src/` | No `print`; `os.environ` only in config.py:112,158, commands/context.py:33, app.py:37; no hardcoded credential in `src/` |
| Dependency audit | `pip_audit -r` on the five pinned runtime dependencies (`--no-deps --disable-pip`) | "No known vulnerabilities found" (transitive packages not audited) |
| Audit of `requirements.txt` as is | `pip_audit -r requirements.txt` | Failed: "requirement pytest is not pinned to an exact version" (REVIEW-003) |
| DB open failure handling | database path pointed at a non-database text file; `check_reachable` called | Raised `employee_app.db.errors.StorageError` (wrapped, no raw sqlite exception) |
| Operator command launch | `python -m employee_app.commands unlock-user bob` from repo root without `PYTHONPATH` | `ModuleNotFoundError: No module named 'employee_app'` (REVIEW-001) |
| Manual browser check, other OS, network file system | Not Run (TASK-045, TASK-046 are open in the report) | Not Run |

## 3. Seven review areas

### 3.1 Correctness: good
Verified in code against requirements and design-review conditions:
- Lockout is one conditional UPDATE that counts, restarts an expired lock and sets the lock in the same statement (`db/lockout.py:25-43`); the success reset is conditional on not-locked (`db/lockout.py:46-57`); a lost conditional update rejects the login (`auth/login.py:55-61,89-90`); a storage failure fails closed to the same generic result.
- NR-12: no write for an already locked account (`auth/login.py:84-85` returns before `_count_failure`); a statement-capturing test exists (`tests/test_login_lockout.py:76`).
- Authentication before CSRF: `auth/guard.py:30-37` returns 302 (page) or 401 (submission) before `csrf.protect()`; `WTF_CSRF_CHECK_DEFAULT=False` (`app.py:69`). 401 carries no `WWW-Authenticate` (`tests/test_errors_headers.py`). `next` is ignored (`routes/auth_routes.py:27`).
- PRG: 303 after create (`routes/employee_routes.py:41`); success message through a fixed flash key.
- Employee and audit rows are written in one `BEGIN IMMEDIATE` transaction (`db/employees.py:45-51`; `db/engine.py:32-34,49-51`); the duplicate pre-check ends before the write (D-25).
- Email uniqueness is case-insensitive through `email_normalized` (casefold) with a unique index (`db/models.py:66`, `validation/email.py:15-17`); the duplicate race is handled by a re-query after an integrity error (`services/employee.py:65-76`).
- Phone: 10 ASCII digits after removing space, hyphen and parentheses; a plus sign is rejected (`validation/phone.py`). Date: strict ISO, real calendar date, not in the past, optional maximum (`validation/date_dept.py`). Limits 100/254/16 KB come from config defaults (`config.py:66`, `validation/limits.py`).
- `unlock-user`: single UPDATE of count and lock only; idempotent; an unknown user gives a clear error and non-zero exit (`commands/accounts.py:77-105`, `db/lockout.py:60-63`); `is_active`, password and `auth_version` untouched (`tests/test_cmd_unlock_user.py:46-60`, `tests/test_unlock_integration.py:40-56`).
- Startup-check table: web checks in `app.py:40-56`; commands use only the core settings group (`commands/context.py:30-45`); `init-db` skips the schema check.
- Missing data rule: the web feature outputs no missing data; the only `Not Found` literal is `NOT_FOUND` in `config.py:30`, defined but unused (REVIEW-008).
No confirmed correctness defect.

### 3.2 Security: good
- Credentials only from environment (`config.py:161`); passwords only from a hidden, confirmed prompt (`commands/cli.py:32-34`); there is no password option. No secret literal in `src/`; test credentials are generated with `secrets` (`tests/conftest.py:52-59`). `WebSettings.secret_key` has `repr=False` (`config.py:62`).
- Hashing: scrypt through Werkzeug; a dummy hash is verified for unknown users (`auth/login.py:79`); the remaining timing difference is the accepted risk NR-02.
- Session: `session.clear()` before login (fixation), HttpOnly, SameSite=Lax, Secure default on, no remember-me, server-side lifetime check and `auth_version` revocation (`auth/session.py`, `auth/loader.py`). CSRF lifetime equals session lifetime (`config.py:174`).
- Headers: nosniff, DENY framing, restrictive CSP, no-store, HSTS when cookies are secure (`routes/errors.py:27-30,52-59,82-83`). Templates rely on autoescaping; no safe-filter or Markup use in `templates/`.
- SQL: only SQLAlchemy constructs. The one f-string SQL (`db/engine.py:34`, BEGIN with a mode) takes the mode only from an internal constant or the default; no user input reaches it.
- Logging: allow-listed fields and a token regex (`logging_setup.py:12-15,43-52`); no username, password, hash or employee data is logged. Residual: tracebacks (REVIEW-005). Signing-key strength is not validated (REVIEW-004).

### 3.3 Error handling: good
Storage errors map to `StorageError` or `IntegrityConflict` with a category only (`db/engine.py:54-75`), parameters hidden (`hide_parameters=True`). Create-employee and login handle `StorageError` on every database call (`services/employee.py`, `auth/login.py`); `load_user` falls back to unauthenticated; a catch-all handler gives a generic 500 page (`routes/errors.py:47-49`); startup and commands raise clear errors naming the setting without values. Bad settings-file JSON or values give `ConfigError` (`config.py:89-100`). Observed: a corrupt database file produced `StorageError`, not a raw exception. A failed create shows the generic 500 page and discards typed values (REVIEW-007).

### 3.4 Test coverage: good
436 tests pass (observed). Positive, negative and boundary cases exist for validation (100/254 limits, 10-digit phone, date boundaries), lockout (concurrency with real connections and a barrier, a deterministic forced interleaving, three fail-closed injection points), duplicate race (the loser must see the email-in-use error), atomicity, auth/CSRF ordering, headers, logging redaction, unlock (AC-16, AC-17, N-20, E-18 by name) and end-to-end AC-01 to AC-10. One `time.sleep` only (`tests/test_lib_sqlite.py:97`, a library characterisation test); no skip or xfail. Gaps: no automated FR/AC traceability check (TASK-041 not written); no browser test (TASK-046, Not Run); concurrency evidence is local Windows only (stated in the report). Tests were read selectively, not every body.

### 3.5 Code clarity: good
Small single-purpose functions; consistent layering (routes, services, validation, db); docstrings cite design decisions. All signatures are annotated (confirmed). Minor nits in REVIEW-006.

### 3.6 DRY: good with minor items
Shared helpers exist for write statements (`db/statements.py`), sessions, validation and error pages. Minor repetition in REVIEW-006.

### 3.7 Dependency safety: acceptable, with gaps
Five runtime dependencies are pinned exactly in `requirements.txt` and all are imported and needed. `pip_audit` on those pins found no known vulnerabilities. Gaps: REVIEW-002, REVIEW-003. No lock file (Not Found).

## 4. Findings

### REVIEW-001 | Medium | Correctness / operability (documentation)
- Files: `README.md` (line 3 only says to install requirements), `docs/ops-notes.md` section 4, `pyproject.toml:6-13`, `src/employee_app/app.py:76`.
- Description: The operator commands and the web app cannot be started from a fresh checkout by following the written instructions. The package is not importable unless installed or `PYTHONPATH=src` is set (pytest works only because of `pytest.ini` `pythonpath = src`). No document says how to run the web app (factory `create_app` only; no WSGI module) or how to install the package. The implementation report lists the missing console script and README text as open decisions.
- Evidence: observed `ModuleNotFoundError: No module named 'employee_app'` for `python -m employee_app.commands unlock-user bob` from the repository root. `docs/ops-notes.md` section 4 gives the command without the setup step. `pyproject.toml` still has `name = "doc_sync"` and a `[project.scripts]` entry `doc_sync = "doc_sync.cli:main"`, a module that does not exist in this tree.
- Impact: An operator or verifier cannot create the first HR Administrator or start the service without guessing; the first-use path (init-db, create-user, run) is not reproducible from the docs.
- Recommendation (developer agent, with a human decision on the console script): document exact steps (`pip install -e .` or `PYTHONPATH=src`, required environment names, `init-db`, `create-user`, how to launch, for example `flask --app employee_app.app:create_app run`, with the development-mode caveat) and run them to confirm. Decide whether to add a console script and fix or remove the stale `doc_sync` entry.

### REVIEW-002 | Low | Dependency safety
- Files: `requirements.txt`, `pyproject.toml:11` (`dependencies = []`), `src/employee_app/commands/cli.py:7`.
- Description: `click` is imported directly but not declared; it is present only as a transitive dependency of Flask (installed 8.5.1). `pyproject.toml` declares no dependencies, so `pip install -e .` would install an app that cannot import Flask.
- Impact: Fragile install; a change in Flask dependencies could break the operator commands.
- Recommendation: declare `click` and the five runtime packages in `pyproject.toml` dependencies, or pin `click` in `requirements.txt`.

### REVIEW-003 | Low | Dependency safety
- File: `requirements.txt:1-2`.
- Description: `pytest>=8.0` and `pip-audit>=2.7` (pre-existing lines) are unpinned, so `pip-audit -r requirements.txt` fails. Transitive packages (WTForms, Click, Jinja2, MarkupSafe, itsdangerous, greenlet and others) are unpinned and there is no lock file. The report says vulnerability scanning was not run.
- Evidence: observed pip-audit error that pytest is not pinned to an exact version. Audit of the five pinned runtime packages with `--no-deps`: no known vulnerabilities (transitive packages not covered; audit of the full installed environment: Not Run).
- Impact: The vulnerability check cannot be automated against the file; transitive versions can drift.
- Recommendation: split runtime and dev requirements or add a constraints/lock file; run `pip-audit` on the full environment before release and record the result.

### REVIEW-004 | Low | Security
- File: `src/employee_app/config.py:161-163`.
- Description: The signing key is only checked for being non-empty; a one-character key is accepted outside testing.
- Impact: A weak key weakens session and CSRF signing (a deployer mistake; no exploit demonstrated).
- Recommendation: require a minimum length (for example 32 characters) outside `testing`, naming only the setting in the error, add a test, and document how to generate a key.

### REVIEW-005 | Low | Security / logging
- Files: `src/employee_app/logging_setup.py:59-65`, `src/employee_app/routes/errors.py:47-49`.
- Description: The module docstring says no field can carry personal data, but `log_server_error` attaches the full traceback (`exc_info=exc`) and the catch-all handler logs any unexpected exception. Storage errors are safe (category-only text, parameters hidden), but the message text of an arbitrary non-storage exception is not controlled.
- Impact: Possible leak of request-derived text into logs through an unforeseen exception message. Not demonstrated; no such path was found in the code read.
- Recommendation: log only the exception class and location for unexpected exceptions, or add a test that an exception carrying a password-like value does not reach the captured log, and soften the docstring claim.

### REVIEW-006 | Low | Code clarity / DRY
- Files: `src/employee_app/auth/login.py:21-34` and `src/employee_app/commands/accounts.py:23-27` (the same pattern of building a fields dict and adding an optional user id, three times); `src/employee_app/services/employee.py:38-40` (`_pre_check` only forwards to `email_exists`); `src/employee_app/auth/loader.py:17-20` (one `except` for two types, then `isinstance` to split them).
- Impact: Small readability cost only.
- Recommendation: a tiny shared helper for the optional user id field, call `email_exists` directly, and use two `except` clauses in `load_user`.

### REVIEW-007 | Informational | Error handling
- File: `src/employee_app/routes/employee_routes.py:44`.
- Description: On a storage failure the user gets the generic 500 page and the entered values are lost, although `CreateResult.values` carries them. This is consistent with the design (generic failure), so it is not a defect.
- Recommendation: optionally re-render the form with a generic banner and preserved values; confirm with the human.

### REVIEW-008 | Informational | Clarity / security
- Files: `src/employee_app/config.py:30` (`NOT_FOUND` defined, unused in `src/`); `src/employee_app/security.py:22-25` with `src/employee_app/auth/login.py:79` (`dummy_hash` is computed lazily, so the first unknown-user login is slower).
- Recommendation: remove or use the constant; optionally precompute the dummy hash at startup. The timing difference is the accepted risk NR-02.

### REVIEW-009 | Informational | Test evidence / report accuracy
- Report claims checked against reality: 436 passed (confirmed, 41.45 s); type hints (confirmed); no secrets (confirmed by grep); changed files (`requirements.txt`, `pytest.ini`, `.gitignore`) consistent with the tree; `src/doc_sync/` absent (confirmed). Open items match the report: TASK-041 traceability script not written, TASK-044/045/046 open, no browser or vulnerability-scan result. No false claim was found. The report claim of 5 repeated concurrency runs was not reproduced here (Not Run).

## 5. Conformance to design-review conditions

| Condition | Result |
|---|---|
| Lockout atomic update | Met (`db/lockout.py:25-43`; concurrency tests pass) |
| NR-12 skip write while locked | Met (`auth/login.py:84-85`; `tests/test_login_lockout.py:76`) |
| Authentication before CSRF | Met (`auth/guard.py:27-38`) |
| 401 without WWW-Authenticate | Met (`tests/test_errors_headers.py`) |
| PRG | Met (303) |
| Atomic employee + audit | Met (`db/employees.py:45-51`; `tests/test_atomicity.py`) |
| Case-insensitive unique email | Met (casefold + unique index) |
| Phone / date / limits | Met |
| unlock-user behaviours | Met |
| Startup-check table | Met (`app.py`, `commands/context.py`, `tests/test_app_startup.py`) |
| No secrets logged or stored; passwords never from env | Met by code reading and grep; tests assert it |

## 6. Verdict and conditions

**APPROVED_WITH_CONDITIONS.** Verification may proceed. Conditions before release (non-blocking for verification): fix or accept REVIEW-001 (run/install documentation); decide REVIEW-002, REVIEW-003 and REVIEW-004; the remaining Low and Informational items are optional.

## 7. Open questions and limitations

- Human decisions: console script and the stale `doc_sync` entry in `pyproject.toml`; dependency split or lock policy; minimum signing-key length; who updates README and CHANGELOG (PR step).
- Not Run: manual browser check (TASK-046), deployment-target checks (TASK-045), network file system, non-Windows platforms, audit of the full installed environment, repeated flakiness runs.
- Written sign-off records for the delegated defaults: Not Found.

## 8. Re-review (delta only: fixes for REVIEW-001 to REVIEW-004, uncommitted in the working tree)

Scope: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` (new), `README.md`, `.gitignore`, `src/employee_app/app.py`, `tests/test_app_startup.py`, `tests/test_config.py`, and anything they could break. Report section 8 of `docs/implementation-report.md` was compared with what was observed.

### 8.1 Observed results

| Check | Result |
|---|---|
| Full suite `.venv/Scripts/python -m pytest -q` | 441 passed in 41.15 s (436 plus 5 new cases, as the developer reported) |
| Editable install | `pip show employee_app`: version 0.1.0, editable location is the repository, requires click, Flask, Flask-Login, Flask-WTF, SQLAlchemy, Werkzeug. I confirmed the existing editable install; I did not re-run `pip install -e .` |
| `employee-admin --help` from a temporary directory, PYTHONPATH unset | Listed create-user, deactivate-user, init-db, unlock-user |
| `python -m employee_app.commands --help` from a temporary directory, PYTHONPATH unset | Works |
| `employee-admin init-db` on a temporary database | Exit 0, "Database schema is ready." |
| `employee-admin unlock-user nobody` | Exit 1, "Unknown username; no change was made" |
| `flask --app employee_app.app:create_app routes` with a 36-character key | Listed the employee routes and static (the login and logout routes were cut by my output filter) |
| Same with key `short` | `StartupError: Setting EMPLOYEE_APP_SECRET_KEY is too short (minimum 32 characters)` (value not printed) |
| `pip-audit -r requirements.txt` (with dependency resolution) | "No known vulnerabilities found" (includes transitive packages; it printed a temp-path warning only) |
| `git status` after tests | Only the expected modified files plus untracked `requirements-dev.txt`; `*.egg-info/` is ignored. No stray db files |
| `create-user` | Not Run (hidden prompt needs an interactive console; the report says the same) |

README commands compared with the real CLI: `init-db`, `create-user`, `deactivate-user USERNAME`, `unlock-user USERNAME`, `python -m employee_app.commands`, `flask --app employee_app.app:create_app run`, and the environment variable names all match `commands/cli.py`, `config.py` and the observed output. The development server `run` itself was not started by me (Not Run); the `routes` command loaded the app.

### 8.2 Status of earlier findings

| Id | Status | Evidence |
|---|---|---|
| REVIEW-001 | Resolved | Package is installable from a clean directory without PYTHONPATH; console script `employee-admin` works; stale `doc_sync` entry removed from `pyproject.toml`; README "Run and install" gives install, variables, init-db, create-user, run and tests, and matches the CLI |
| REVIEW-002 | Resolved | `pyproject.toml` declares Flask, Flask-Login, Flask-WTF, SQLAlchemy, Werkzeug and `click==8.5.1`; `requirements.txt` also lists `click==8.5.1` |
| REVIEW-003 | Partially resolved | `requirements.txt` is now all exact pins and `pip-audit -r requirements.txt` runs and reports no known vulnerabilities; `requirements-dev.txt` pins pytest and pip-audit. Transitive packages are still not pinned and there is no lock file (Low, left open) |
| REVIEW-004 | Resolved | `app.py:43-46` rejects a key under 32 characters at web startup with a message naming only the setting; `MIN_SECRET_KEY_LENGTH` at `app.py:28`; parametrised tests added (0, 31 rejected; 32, 33, 64 accepted) and pass. The check is in the web startup only, so operator commands, which need no key, are not affected (observed: init-db and unlock-user ran without a key) |
| REVIEW-005 | Accepted (by the user) | Not re-checked; unchanged |
| REVIEW-006 | Accepted (by the user) | Unchanged |
| REVIEW-007 | Accepted (by the user) | Unchanged |
| REVIEW-008 | Accepted (by the user) | Unchanged |
| REVIEW-009 | Accepted (by the user) | The report's claim of 441 passed after the fixes is confirmed |

### 8.3 New findings

- REVIEW-010 | Informational | Dependency safety. `pyproject.toml` pins runtime dependencies with `==` (and `click==8.5.1`), duplicating `requirements.txt`. Fine for an application, but two places must be kept in step and it blocks installing alongside other packages. Recommendation: keep as is, or make one file the source of truth. No action required.
- No regression found in the delta: the full suite passes and the earlier design-review conformance points were not touched.

### 8.4 Updated verdict

**APPROVED_WITH_CONDITIONS.** No blocking finding remains. Remaining non-blocking items: REVIEW-003 residual (transitive pins and lock file; the optional decision is for a human), the accepted items REVIEW-005 to 009, and REVIEW-010 (informational).

Human decision still open: whether a lock file or constraints file for transitive dependencies is wanted; production server, deployment target and browser check remain Not Found / Not Run as before.
