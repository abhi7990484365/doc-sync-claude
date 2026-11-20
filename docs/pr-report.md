# Pull Request Report: SCRUM-101 Add a New Employee (Step 8, preparation only)

Source branch: `feature/doc-sync-claude`. Target branch: `main`. Branch HEAD at preparation time: `f43ffb0`. Unknown = `Not Found`.

PR Status: Not Created; PR Number: Not Found; PR URL: Not Found

Nothing was committed, pushed or opened in this step. Explicit human approval is still required before any push or PR creation.

## Proposed PR title

`feat: add employee web app with HR add-employee form, login and operator commands (SCRUM-101)`

## Summary

This PR adds the `employee_app` Flask web application for SCRUM-101: a login-protected form where an HR Administrator adds a new employee (seven validated fields), with every successful creation written together with an audit record in one database transaction. It also adds login with lockout, logout, and the `employee-admin` operator commands (init-db, create-user, deactivate-user, unlock-user) needed to run it. Verification finished as VERIFIED_WITH_LIMITATIONS: 441 tests passed, no defects, with the limitations listed below.

## Changes Made

Evidence: `git diff main...HEAD --stat` reports 151 files changed (13192 insertions, 222 deletions) over the committed history, plus 18 modified, uncommitted files in the working tree (`git diff --stat`: 188 insertions, 95 deletions). The working-tree changes must be committed (or deliberately left out) before the PR is opened.

### Application code (committed): `src/employee_app/`

| Area | Files | Purpose |
|---|---|---|
| App factory and config | `app.py`, `config.py`, `extensions.py`, `clock.py`, `logging_setup.py`, `security.py`, `__init__.py` | Settings from environment variable names, signing-key length check, startup checks, logging without secrets, security headers |
| Database | `db/` (`engine.py`, `models.py`, `employees.py`, `users.py`, `lockout.py`, `verify.py`, `statements.py`, `errors.py`, `__init__.py`) | SQLite via SQLAlchemy, employee, user and audit tables, atomic employee-plus-audit write, lockout state |
| Authentication | `auth/` (`guard.py`, `loader.py`, `login.py`, `session.py`) | Login, session handling, role guard, lockout after repeated failures |
| Routes and services | `routes/` (`auth_routes.py`, `employee_routes.py`, `errors.py`), `services/employee.py` | `GET/POST /employees/new`, login, logout, error pages (generic 401/403/405/413/500) |
| Validation | `validation/` (name, email, phone, date, department, password, username, limits, messages) | Field rules, trimming, normalisation, length limits |
| Operator commands | `commands/` (`cli.py`, `accounts.py`, `context.py`, `__main__.py`, `__init__.py`) | `employee-admin` commands: init-db, create-user, deactivate-user, unlock-user |
| Templates and static | `templates/` (base, employee_form, login, error), `static/` (`form.js`, `style.css`) | Server-rendered pages, no inline script |

### Tests (committed): `tests/`

43 Python files in `tests/` (for example `test_e2e_add_employee.py`, `test_auth_*.py`, `test_login_lockout.py`, `test_cmd_*.py`, `test_atomicity.py`, `test_duplicate_race.py`, `test_lockout_concurrency.py`, `test_unlock_integration.py`, `test_validation_*.py`, `test_config.py`, `test_app_startup.py`, `test_security.py`, `test_perf_smoke.py`) plus helpers `conftest.py`, `helpers.py`, `web_helpers.py`, `cmd_helpers.py`. They cover every FR, NFR and AC with an executed test or an explicit Not Run mark (see `docs/verification-report.md` section 4).

### Packaging and configuration (committed)

| File | Purpose |
|---|---|
| `pyproject.toml` | Makes `employee_app` installable; defines the `employee-admin` console script |
| `requirements.txt` | Pinned runtime dependencies |
| `requirements-dev.txt` | Pinned test and audit tools (pytest, pip-audit) |
| `pytest.ini` | Registers the `informative` marker |
| `.gitignore` | Rewritten; covers `.env`, `*.db`, `*.sqlite*`, WAL files, `*.egg-info/`, `.venv/` |
| `README.md` | "Run and install" section for the web app (environment variable names only) |
| `CHANGELOG.md` | Changelog entry for this change (see below) |
| `CLAUDE.md` | Rewritten for the SCRUM-101 employee web app (package `src/employee_app/`, branch `feature/doc-sync-claude`); the earlier text described the doc_sync CLI |

### Pipeline documents (committed): `docs/`

`user-story.md`, `requirements.md`, `architecture.md` (Revision 3; the real name, not `architecture-design.md`), `design-review.md`, `impl-plan.md`, `implementation-report.md`, `code-review.md`, `ops-notes.md`, `test-output.txt`, `sdlc-state.md`, `pr-description.md`, `verification-report.md`. The legacy doc_sync documents were intentionally replaced (recoverable from git history). `src/doc_sync/` and `docs/PROJECT_DOC.md` do not exist in this tree; the doc_sync CLI is not part of this PR.

### Pipeline configuration (committed): `.claude/`, `.mcp.json`, `.vscode/settings.json`

Agents, commands, rules, skills, hooks, `settings.json` and `sdlc-common.md` that implement the agentic SDLC pipeline.

### Uncommitted working-tree changes (18 files, to be committed deliberately)

| Files | Change | Purpose |
|---|---|---|
| `.claude/agents/sdlc-code-reviewer.md`, `sdlc-developer.md`, `sdlc-pr-agent.md`, `sdlc-verification-agent.md`; `.claude/commands/sdlc-pr.md`; `.claude/rules/rule-code-review.md`, `rule-implementation.md`, `rule-pull-request.md`, `rule-verification.md`; `.claude/skills/code-review/SKILL.md`, `implementation/SKILL.md`, `pull-request/SKILL.md`, `verification/SKILL.md` | Modified (small line edits) | Branch name `feature/doc-sync` updated to `feature/doc-sync-claude` and package name `doc_sync` to `employee_app`, resolving inconsistency (c) in the verification report |
| `.claude/hooks/pre_bash_guard.py` | Modified (1 line) | Block message now names `feature/doc-sync-claude` (message text only; the guard logic is unchanged) |
| `docs/code-review.md`, `docs/implementation-report.md` | Modified (1 to 2 lines each) | Small consistency fixes noted in verification |
| `docs/verification-report.md` | Rewritten | Step 7 verification report (VERIFIED_WITH_LIMITATIONS) |
| `docs/sdlc-state.md` | Modified | Pipeline state through step 7 (maintained by the orchestrator) |

Also changed in this step, not yet committed: `docs/pr-report.md` (new) and `CHANGELOG.md` (new entry).

## Test Evidence

All results below are from `docs/verification-report.md` section 3 (Step 7 run on Python 3.11.9, repository `.venv`, HEAD `f43ffb0`). No CI link exists: `Not Found`. The tests were not re-run in this step.

| Command | Result |
|---|---|
| `.venv/Scripts/python -m pytest -q` | 441 passed, 0 failed, 0 skipped, 42.03 s |
| `.venv/Scripts/python -m pytest -q -m "not informative"` | 439 passed, 2 deselected (perf tests), 41.29 s |
| `pytest -q -rs` on `test_perf_smoke.py`, `test_e2e_add_employee.py`, `test_unlock_integration.py`, `test_lockout_concurrency.py`, `test_duplicate_race.py` | 56 passed, 14.22 s |
| `.venv/Scripts/employee-admin --help` | Lists create-user, deactivate-user, init-db, unlock-user (matches README) |

Spot checks against the running app (Flask test client, temporary database, generated throw-away password, all removed afterwards), observed results:

- Unauthenticated `GET /employees/new` returned 302 to `/login`; unauthenticated `POST` returned 401 with and without a token; employee rows stayed at 0.
- Five wrong logins locked the account; the correct password afterwards still returned the login page (not logged in).
- Valid creation with today's date and phone `555 123-4567` returned 303; one employee row (phone stored as 10 digits) and one audit row were written.
- A duplicate email with different case, a yesterday date and a `+1 ...` phone were each rejected (200); `(555) 123-4567` was accepted (303). Final counts: 2 employees, 2 audit rows.
- `POST /logout` with token returned 303; `GET /employees/new` then 302; `GET /logout` returned 405.

Not Run (reasons in `docs/verification-report.md` section 9): manual four-browser check (NFR-5, TASK-046); deployment-target and HTTPS checks (TASK-045); interactive hidden-prompt `create-user` (the same code path is covered through `create_account` tests); performance under real load (NFR-3); network file system and non-Windows platforms; `flask run`, `pip install -e .` and `pip-audit` re-runs in the verification step (earlier results are in `docs/implementation-report.md` and `docs/code-review.md`); repeated flakiness runs of concurrency tests; secret scan with a dedicated scanner (only a pattern search was done, which found no real credentials).

## Known Limitations

- Department names are `Not Found`. The production app refuses to start with an empty department list, so a human must supply the names (via `EMPLOYEE_APP_SETTINGS_FILE`) before release. Tests use "Test Dept A/B" only (TASK-044).
- Deployment target and production server are `Not Found`; HTTPS termination and production setup are not verified (TASK-045).
- There is no lock file; transitive dependencies are not pinned (REVIEW-003 residual).
- Not Run: manual browser check (Chrome, Edge, Firefox, Safari; NFR-5), interactive `create-user` prompt, performance under load, network file system and non-Windows platforms (see Test Evidence).
- Risk: Flask-WTF enforces a strict `Referer` check over HTTPS; this needs checking on the deployment target.
- Defaults adopted by delegation (field limits, lockout, logout, repeated submit) have no written sign-off record (`Not Found`). Error message wording and several edge-case behaviours (E-10, E-13, E-14, E-15) are `Not Found` in the requirements.
- Scope additions beyond the original story, approved during the pipeline: login, logout and account lockout, operator commands for user management, and `unlock-user` (FR-14, FR-16, FR-18).
- TASK-041 (automated traceability script and architecture amendment) was not done; the traceability matrix is manual. NFR-2 retention and PII rules are `Not Found`.
- Concurrency evidence comes from one local Windows machine.
- `docs/PROJECT_DOC.md` and `src/doc_sync/` do not exist; the doc_sync CLI is not part of this PR. The existing README top section and the older `CHANGELOG.md` doc_sync entries still describe that earlier work.
- Code-review items REVIEW-005 to REVIEW-010 remain accepted or informational as recorded in `docs/code-review.md`.

## Reviewer Checklist

- [ ] Requirements FR-1 to FR-18, NFR-1 to NFR-5 and AC-01 to AC-17 in `docs/requirements.md` are addressed (see the matrix in `docs/verification-report.md`).
- [ ] The implementation follows `docs/architecture.md` (Revision 3) and the accepted design-review conditions.
- [ ] Employee and audit record are written in one transaction; no audit row exists after a rejected submission.
- [ ] Authentication, CSRF, lockout and logout behave as specified; unauthenticated requests get 302 or 401 and never write data.
- [ ] Error handling is appropriate: error pages show no stack text, storage failure gives a generic 500, startup fails clearly on missing config or database.
- [ ] No secrets are exposed: only environment variable names appear in code, docs and README; `.gitignore` covers `.env` and database files.
- [ ] Tests cover positive, negative and boundary cases; run `python -m pytest -q` and confirm 441 passed.
- [ ] The README "Run and install" section matches the real commands and environment variable names.
- [ ] The `.claude/` branch and package name updates and the `CLAUDE.md` rewrite are intended.
- [ ] The old doc_sync entries in `CHANGELOG.md` and the README intro are acceptable or should be removed.
- [ ] Known limitations are accepted, and owners are named for department names, deployment target, lock file and the browser check.
- [ ] The 18 uncommitted working-tree files were committed on purpose, with Conventional Commit messages.
- [ ] Changelog is included.

## Changelog entry

See `CHANGELOG.md`, section "[Unreleased] SCRUM-101 Add a New Employee (2026-11-20)". No version number was assigned (`Not Found`).

## Human decisions needed before creating the PR

1. Approve committing the 18 uncommitted files plus `docs/pr-report.md` and `CHANGELOG.md`, and approve pushing `feature/doc-sync-claude`.
2. Decide whether the older doc_sync entries in `CHANGELOG.md` and the README intro stay, since that code is not in this tree.
3. Approve the PR title and description, then explicitly authorise PR creation.
4. Decide who supplies department names, the deployment target, a lock file decision and the browser check.
