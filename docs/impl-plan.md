# Implementation Plan: SCRUM-101 Add a New Employee

Note: Replaces the previous doc_sync CLI implementation plan by user decision. Nothing is carried over.
Convention: "Confirmed" = stated in approved requirements or architecture. "Default" = a requirements value adopted by user delegation. "Proposal" = this plan's suggestion, not an approved decision. Unknown = `Not Found`.
This plan contains no application code and records no execution results. Status of every task is "Not Started" or "Blocked".

## 1. Planning Overview

| Item | Value |
|---|---|
| Story | SCRUM-101 Add a New Employee |
| Date | 2026-11-20 |
| Inputs | `docs/requirements.md` (approved 2026-11-20, includes FR-18, AC-16, AC-17), `docs/architecture.md` Revision 3 (the stage command calls it `architecture-design.md`; the real file is `docs/architecture.md`; Revision 3 approved by the user 2026-11-20 per its section 13), `docs/design-review.md` (Review 3, verdict APPROVED_WITH_CONDITIONS, sections 19 to 24) |
| Rules applied | `CLAUDE.md`, `.claude/rules/rule-implementation-planning.md`, `.claude/skills/implementation-planning/SKILL.md` |
| Branch | `feature/doc-sync-claude` only. No commit or push to `main`. This plan creates no commits. |
| Task count | 48 (TASK-001 to TASK-048) |
| Code rules for every task | Python 3.11; type hints on every function signature; small single-purpose functions; shared helper instead of duplicated logic; pytest in `tests/` with a test for every new behaviour; missing data written as exactly `Not Found`; credentials only from environment variables; no secret in any file, log, commit or PR; no crash on API/storage failure, missing file or empty database |

### 1.1 Design-review conditions carried into the plan

| Item | Handling | Task |
|---|---|---|
| NR-12 skip lockout write while a lock is active | Implementation task (user decision, architecture 13) | TASK-028 |
| NR-13 mapping for FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18; tests for password unchanged and deactivated-stays-blocked after unlock | Tests plus an amendment request (architecture text is not edited by this plan) | TASK-021, TASK-022, TASK-041 |
| NR-14 WAL operational notes; race test asserts a defined outcome | Notes task plus an asserting test | TASK-042, TASK-035 |
| NR-15 operator action logging, no usernames or secrets | Task | TASK-043 |
| Lockout concurrency and fail-closed tests | Mandatory tests | TASK-033, TASK-034 |
| D-25 transaction scope | Persistence and service tasks | TASK-017, TASK-030, TASK-035 |
| D-24 startup-check table per entry point | Tasks | TASK-018, TASK-023 |
| OQ-A15 401 without `WWW-Authenticate` (approved: keep 401) | Task | TASK-024 |
| `unlock-user` with unknown username: error exit, no change (approved) | Task | TASK-021 |
| Library behaviours marked "verify at implementation" | Verification tasks, before dependent work | TASK-003, TASK-004 |
| DR-24 `CLAUDE.md` still describes a CLI | Ask the user; no silent edit | TASK-001 |
| NR-09 residual (written sign-off record) | Human decision DEC-5, not a task | section 8.2 |

### 1.2 Items not planned (not in approved scope)
Edit, delete, bulk import, payroll (out of scope); web user-management screen; reactivation, password reset, forgotten-password procedure (OQ-17, OQ-19: `Not Found`); roles other than HR Administrator (OQ-16); audit viewing screen, retention and format (OQ-18); per-source throttle; encryption at rest; load testing (OQ-12); E-10 and E-13 behaviours (unmapped in architecture); vulnerability scanning (`Not Found`). Validation message wording and error page wording are `Not Found`; the architecture Proposal (short generic text, no technical detail) is used.

## 2. Architecture Reference

| Id | Component | Responsibility (architecture section 5) |
|---|---|---|
| C-1 | App factory and web startup checks | Build the Flask app; web-only startup checks (D-24) |
| C-2 | Authentication and authorisation | Login, lockout, logout, session validation, role check, ordered CSRF |
| C-3 | Web routes and error handlers | HTTP only; routes `GET/POST /login`, `POST /logout`, `GET/POST /employees/new`; error pages; headers |
| C-4 | Validation and normalisation | Pure functions; all field rules and the password rule |
| C-5 | Employee service | Create-employee use case; duplicate pre-check; owns the commit |
| C-6 | Persistence | Models, engine, sessions, schema verification, conditional updates |
| C-7 | Configuration | Environment and non-secret settings, grouped validation |
| C-8 | Clock | Server local date; current UTC time |
| C-9 | Templates and static assets | Login page, Add Employee page, logout form, error pages |
| C-10 | Admin commands | `init-db`, `create-user`, `deactivate-user`, `unlock-user` |
| C-11 | Logging | Logging setup and redaction rules |

Dependency rules to preserve: C-4 and C-8 import neither Flask nor the database; C-4 receives today's date, limits and department list from C-5; routes never call the database directly; C-10 does not call C-1 and loads only the database settings group (D-24).

Stack (approved D-1 to D-14): Flask 3.x, Flask-Login (remember-me not used), Flask-WTF for CSRF only, SQLAlchemy 2.x, SQLite, Werkzeug scrypt, Click, pytest. Versions are pinned at implementation (TASK-002).

## 3. Implementation Workstreams

| Workstream | Purpose | Tasks |
|---|---|---|
| WS-1 Governance and setup | User decisions, scaffolding, library verification | TASK-001 to TASK-004 |
| WS-2 Foundations and pure rules | Clock, configuration, logging, validation | TASK-005 to TASK-013 |
| WS-3 Persistence | Schema, verification, lockout queries, employee and audit write | TASK-014 to TASK-017 |
| WS-4 Operator commands | `init-db`, `create-user`, `deactivate-user`, `unlock-user` | TASK-018 to TASK-022 |
| WS-5 Web application | Factory, headers and errors, auth, service, routes, templates | TASK-023 to TASK-032 |
| WS-6 Cross-cutting tests | Concurrency, fail-closed, race, atomicity, auth, end-to-end, security | TASK-033 to TASK-040 |
| WS-7 Operations, packaging and final checks | Traceability request, notes, operator logging, blocked items, final verification | TASK-041 to TASK-048 |

## 4. Prioritized Task Breakdown

Priority meaning: P0 foundational work that blocks later tasks; P1 essential functionality; P2 supporting or quality; P3 optional. Test file names are Proposals. `<APP_PKG>` is the application package path, which is not fixed by the architecture and depends on TASK-001. All tasks except TASK-041 are gated by TASK-001 through TASK-002.

### WS-1 Governance and setup

#### TASK-001 Ask the user: `CLAUDE.md` and repository layout (DR-24)
- Description: Ask the user (through the orchestrator; this agent cannot talk to the user) (a) whether and how to update `CLAUDE.md`, which still describes a doc_sync CLI, `src/doc_sync/` and `docs/PROJECT_DOC.md`; (b) where the Flask application package lives (the architecture defines no package layout); (c) the application package name and the `tests/` layout. Options may be offered as recommendations only. Do not edit `CLAUDE.md` or move files before the answer.
- Priority: P0. Every code path and test location depends on the answer.
- Dependencies: none.
- Expected files or components: decision record returned to the orchestrator; `CLAUDE.md` and layout changes only after approval.
- Testing requirements: none.
- Acceptance criteria: a written user answer exists for (a), (b) and (c); `CLAUDE.md` is unchanged until that answer; the chosen package path replaces `<APP_PKG>` in later tasks.
- Status: Blocked (needs user decision DEC-1).

#### TASK-002 Project scaffolding and dependency pinning
- Description: Create the package skeleton per the TASK-001 answer, pytest configuration, pinned dependencies compatible with Python 3.11, and ignore rules so database files (including `-wal` and `-shm`) and any `.env` with values are never committed.
- Priority: P0. Foundation for all work.
- Dependencies: TASK-001.
- Expected files or components: `<APP_PKG>/__init__.py`, `tests/conftest.py`, dependency file, pytest config, `.gitignore` additions.
- Testing requirements: smoke test that the package imports and pytest collects.
- Acceptance criteria: package imports on Python 3.11; `pytest` collects with zero errors; ignore rules cover `*.db`, `*.sqlite*`, `*-wal`, `*-shm`, `.env`; no secret value in any file; dependency versions pinned.
- Status: Not Started.

#### TASK-003 Verify library behaviour: CSRF, hook ordering, token lifetime, remember-me
- Description: Verify with small characterization tests the points the architecture marks "verify at implementation": (a) the extension's automatic CSRF check can be turned off and the check called manually (D-5); (b) a before-request authentication check runs before the manual CSRF check and body is not read for unauthenticated requests; (c) CSRF token lifetime can be set equal to the session maximum lifetime (C-7); (d) Flask-Login remember-me cookie is not issued; (e) cookie flags HttpOnly, SameSite=Lax, Secure from `SESSION_COOKIE_SECURE`. Report results; an outcome that contradicts the architecture goes to the orchestrator and is not worked around silently.
- Priority: P0. TASK-025 to TASK-029 rely on these behaviours.
- Dependencies: TASK-002.
- Expected files or components: `tests/test_lib_csrf_session.py`.
- Testing requirements: positive and negative characterization tests per point (a) to (e).
- Acceptance criteria: each of (a) to (e) has a test; each test outcome is reported as confirmed or contradicted; no assumption stays unverified.
- Status: Not Started.

#### TASK-004 Verify library behaviour: SQLAlchemy and SQLite
- Description: Verify with characterization tests on a temporary file database: (a) `hide_parameters` keeps statement values out of exception text (D-21); (b) a write transaction that begins as a write waits for the busy wait instead of failing late (D-25); (c) whether an update that matches no row still takes the writer lock (NR-12); (d) write-ahead journal mode is activated and coexists with two connections; (e) foreign keys can be enabled; (f) an integrity error on the unique index is distinguishable by re-query (D-20).
- Priority: P0. TASK-014, TASK-017 and TASK-035 depend on the findings.
- Dependencies: TASK-002.
- Expected files or components: `tests/test_lib_sqlite.py`.
- Testing requirements: two-connection tests on a temporary file database (not in-memory).
- Acceptance criteria: each of (a) to (f) has a test with its observed outcome reported; contradictions are reported to the orchestrator.
- Status: Not Started.

### WS-2 Foundations and pure rules

#### TASK-005 C-8 Clock
- Description: Two functions: server local date ("today", FR-7, OQ-4) and current UTC time (audit, lock expiry, session issue time). Replaceable in tests.
- Priority: P0. Required by validation callers, lockout, sessions and audit.
- Dependencies: TASK-002.
- Expected files or components: `<APP_PKG>/clock.py`; fixed-clock fixture in `tests/conftest.py`.
- Testing requirements: unit tests for both functions, fixture replacement, date-boundary case (E-10) using a fixed instant.
- Acceptance criteria: functions typed; UTC value is timezone-aware; fixture can pin both date and time; module imports neither Flask nor the database.
- Status: Not Started.

#### TASK-006 C-7 Configuration
- Description: Read settings from environment variables and a non-secret settings file; typed values; groups validated separately (database group; web group). Defaults per architecture C-7 table (name length 1 to 100, email 254, body 16 KB, no maximum future date, 5 failures, 15 minutes, password minimum 12, session lifetime 8 hours, CSRF lifetime equal to session lifetime, busy wait 2 seconds, trusted proxies 0, slow-request 3 seconds). Department list defaults to empty (names `Not Found`). Error text names the setting and never prints values. Variable names are decided here (Proposal).
- Priority: P0. Every component reads configuration.
- Dependencies: TASK-002.
- Expected files or components: `<APP_PKG>/config.py`; `tests/test_config.py`.
- Testing requirements: defaults match the table; each missing or invalid setting fails fast naming the setting; messages contain no secret value; operator group requires only the database location; passwords are never read from the environment.
- Acceptance criteria: all listed tests pass; no secret is stored in any file; allowed-characters rule is absent (`Not Found`, none applied).
- Status: Not Started.

#### TASK-007 C-11 Logging setup and redaction helpers
- Description: Standard logging setup with one-line messages. Helpers or rules ensure passwords, hashes, cookies, CSRF tokens, signing key, database credentials, attempted usernames and employee personal data (names, email, phone) are never logged; ids are logged instead. Log events listed in C-11.
- Priority: P1. Needed by auth, service and commands; not a blocker for pure rules.
- Dependencies: TASK-002.
- Expected files or components: `<APP_PKG>/logging_setup.py`; `tests/test_logging.py`.
- Testing requirements: captured logs for sample events contain only ids and categories; stack traces appear only in server logs.
- Acceptance criteria: no test log capture contains a password, hash, username or employee value; logging module has typed signatures.
- Status: Not Started.

#### TASK-008 C-4 Trim and text-field rules
- Description: Shared trim helper (Unicode-aware strip) and field rules for First Name, Last Name and Job Title: required, whitespace-only counts as empty (FR-3), 1 to 100 characters after trim counted in code points (FR-15). Limits are passed in. Returns per-field errors; never raises for user input. Allowed characters: `Not Found`, none applied.
- Priority: P1. Core rules; basis for other field rules.
- Dependencies: TASK-002.
- Expected files or components: `<APP_PKG>/validation/` (module layout Proposal); `tests/test_validation_text.py`.
- Testing requirements: N-1, N-2 (per field), E-6, E-7, N-18, P-12 boundary lengths 1, 100, 101, accented names; no Flask or database import.
- Acceptance criteria: boundary and whitespace tests pass; the module imports neither Flask nor the database.
- Status: Not Started.

#### TASK-009 C-4 Email rules and normalisation
- Description: Required; at most 254 characters; basic local@domain.tld (exactly one `@`, non-empty local part, domain with at least one dot and non-empty labels, no whitespace); `email_normalized` is the trimmed email through `casefold()` (D-3). Uses the TASK-008 trim helper.
- Priority: P1. FR-4, FR-5.
- Dependencies: TASK-008.
- Expected files or components: same validation package; `tests/test_validation_email.py`.
- Testing requirements: N-3 (no `@`, no domain, spaces), E-4 (leading and trailing whitespace), 254 and 255 characters, case pairs including non-ASCII.
- Acceptance criteria: every listed case passes; normalised value of `Jane.Doe@Example.com` equals that of `jane.doe@example.com`.
- Status: Not Started.

#### TASK-010 C-4 Phone rules
- Description: Required; reject if it contains `+`; remove spaces, dashes and parentheses; remainder must be exactly 10 ASCII digits; store the 10 digits (D-13).
- Priority: P1. FR-6.
- Dependencies: TASK-008.
- Expected files or components: same validation package; `tests/test_validation_phone.py`.
- Testing requirements: P-3, P-6 `(555) 123-4567`, N-5 (9 digits, 11 digits, letters, empty, `+1 555 123 4567`), Arabic-Indic digits, Unicode dashes.
- Acceptance criteria: all listed cases give the expected result; non-ASCII digits are rejected.
- Status: Not Started.

#### TASK-011 C-4 Department and joining date rules
- Description: Department must be in the supplied list (FR-11). Joining date: real calendar date in ISO `YYYY-MM-DD`, not before the supplied today, no maximum (Default). Both come from caller-supplied values.
- Priority: P1. FR-7, FR-11.
- Dependencies: TASK-008.
- Expected files or components: same validation package; `tests/test_validation_date_dept.py`.
- Testing requirements: yesterday rejected (N-6), today and tomorrow accepted (P-5), far-future accepted (P-13, E-2), 30 February and unparseable input (E-11), department outside the list rejected.
- Acceptance criteria: all listed cases pass using an injected date; no clock import.
- Status: Not Started.

#### TASK-012 C-4 Aggregate employee validation
- Description: One function combining the field rules; trims all seven fields, collects all errors at once (N-10, AS-5), returns cleaned values plus `email_normalized` or the error map.
- Priority: P1. Used by C-5.
- Dependencies: TASK-009, TASK-010, TASK-011.
- Expected files or components: validation package; `tests/test_validation_employee.py`.
- Testing requirements: all-empty form gives seven errors (N-1); several simultaneous invalid fields (N-10); one valid case returns cleaned values.
- Acceptance criteria: error map keyed by field; never raises for bad user input.
- Status: Not Started.

#### TASK-013 C-4 Password rule
- Description: Non-empty and at least the configured minimum length (12, FR-16); no composition rules. Pure function used by `create-user`.
- Priority: P1. FR-16, N-17.
- Dependencies: TASK-002.
- Expected files or components: validation package; `tests/test_validation_password.py`.
- Testing requirements: empty, 11 and 12 characters.
- Acceptance criteria: 11 rejected, 12 accepted, empty rejected; error text contains no password.
- Status: Not Started.

### WS-3 Persistence

#### TASK-014 C-6 Models, engine and session lifecycle
- Description: Tables User, Employee, AuditRecord per architecture 6.1, including unique indexes on `user.username_normalized`, `employee.email_normalized` and `audit_record.employee_id`; column sizes match limits; foreign keys on; busy wait from configuration; parameter hiding; write-ahead journal mode (Proposal, D-25, subject to TASK-004 and TASK-042); one scoped session per request, always closed, uncommitted work rolled back.
- Priority: P0. Persistence blocks commands, auth and service.
- Dependencies: TASK-002, TASK-004, TASK-006.
- Expected files or components: `<APP_PKG>/db/` (models, engine, session); `tests/test_db_schema.py`.
- Testing requirements: schema creation on a temporary file database; unique indexes reject duplicates; foreign keys enforced; session closed after request; one audit row per employee enforced.
- Acceptance criteria: tests for each listed item pass; no update or delete operation for audit rows or employees exists.
- Status: Not Started.

#### TASK-015 C-6 Schema verification
- Description: Function that checks required tables and unique indexes exist (`employee.email_normalized`, `user.username_normalized`, `audit_record.employee_id`) with clear messages that name the object and print no values. Used by web startup, `init-db` post-condition and user commands.
- Priority: P0. Guards the only uniqueness guarantee (FR-5).
- Dependencies: TASK-014.
- Expected files or components: persistence package; `tests/test_db_verify.py`.
- Testing requirements: passes on a full schema; fails for a missing table; fails for a missing unique index; fails on an empty database.
- Acceptance criteria: each failing case returns a non-secret message naming the missing object.
- Status: Not Started.

#### TASK-016 C-6 Lockout, unlock and `auth_version` conditional updates
- Description: Query functions as single statements: failure update (counts, resets after expired lock, sets `locked_until` at the limit, no change while locked); success update (reset count and clear lock only if not locked at that moment, reports whether a row changed); unlock (sets count 0 and `locked_until` null in one update); atomic `auth_version = auth_version + 1`; lock-state read. Lockout updates commit in their own short transaction. UTC time is passed in.
- Priority: P1. FR-16, FR-18, D-15, D-16.
- Dependencies: TASK-014, TASK-005.
- Expected files or components: persistence package; `tests/test_db_lockout.py`.
- Testing requirements: sequential cases: 5th failure sets the lock; no change while locked; expired lock restarts count at 1; success resets; success update returns no-row when locked; unlock clears both fields; two increments from separate connections are both counted.
- Acceptance criteria: all listed cases pass; the count never exceeds the limit through the statements.
- Status: Not Started.

#### TASK-017 C-6 Employee and audit write plus duplicate pre-check
- Description: Duplicate pre-check as a read whose transaction ends before the write begins (D-25); one write transaction begun as a write that inserts Employee and AuditRecord and commits; on integrity error roll back and expose a re-query for `email_normalized`.
- Priority: P1. FR-5, FR-8, FR-13, D-7, D-25.
- Dependencies: TASK-014, TASK-004.
- Expected files or components: persistence package; `tests/test_db_employee_write.py`.
- Testing requirements: successful write creates one employee and one audit row; pre-check true/false; integrity error rolls back both rows; read transaction is closed before the write starts.
- Acceptance criteria: listed tests pass; no partial row after an injected failure.
- Status: Not Started.

### WS-4 Operator commands

#### TASK-018 C-10 Command context, `init-db` and D-24 startup-check table
- Description: Command context that loads only the database settings group and C-6, without calling the web app factory. `init-db` creates the schema on an empty or existing database and verifies it afterwards. User commands require database reachable and verified schema. No signing key, department list, cookie or debug settings required.
- Priority: P0. Bootstrap path; without it no account can exist.
- Dependencies: TASK-006, TASK-007, TASK-014, TASK-015.
- Expected files or components: `<APP_PKG>/commands/` (Click group); `tests/test_commands_context.py`.
- Testing requirements: `init-db` succeeds on an empty database with no signing key and no department list; verification passes afterwards; `init-db` is repeatable; user commands refuse a database without the schema (non-zero exit, clear message); commands never import the web factory.
- Acceptance criteria: each D-24 table cell for commands is covered by a test; output contains no secret.
- Status: Not Started.

#### TASK-019 `create-user`
- Description: Username and password from an interactive prompt only (password hidden, entered twice); never from environment or arguments. Username trimmed, case-folded, capped at 100 characters; password checked by TASK-013 then hashed (Werkzeug scrypt); role `hr_administrator`, `auth_version` 0.
- Priority: P1. FR-12, AC-11.
- Dependencies: TASK-018, TASK-013.
- Expected files or components: commands package; `tests/test_cmd_create_user.py` (Click test runner).
- Testing requirements: a password environment variable is ignored; weak password rejected (N-17); duplicate username including case-only rejected; stored hash differs from password; output never contains the password; mismatched confirmation rejected.
- Acceptance criteria: all listed tests pass; non-zero exit for each rejection.
- Status: Not Started.

#### TASK-020 `deactivate-user`
- Description: Sets `is_active` false and increments `auth_version` atomically so open sessions end on the next request. Unknown username: error, non-zero exit, no change (same pattern as TASK-021; architecture lists the unknown-username case for the commands).
- Priority: P1. FR-12, AC-12.
- Dependencies: TASK-018, TASK-016.
- Expected files or components: commands package; `tests/test_cmd_deactivate_user.py`.
- Testing requirements: deactivation sets the flag and bumps `auth_version`; repeat run is safe; unknown username errors.
- Acceptance criteria: listed tests pass; no password or hash printed.
- Status: Not Started.

#### TASK-021 `unlock-user` (FR-18)
- Description: Clears `failed_login_count` and `locked_until` in one update via the TASK-016 query. Idempotent. Does not change `is_active`, password or `auth_version`. Unknown username: clear error, non-zero exit, no change (approved 2026-11-20; requirements E-18 still `Not Found`, so this is recorded as an approved Proposal).
- Priority: P1. AC-16, AC-17, P-14, P-15, E-18.
- Dependencies: TASK-018, TASK-016.
- Expected files or components: commands package; `tests/test_cmd_unlock_user.py`.
- Testing requirements: clears count and lock of a locked account; second run gives the same result; unlocked account unchanged (including `is_active`, password hash, `auth_version`); unknown username gives non-zero exit and changes no row; output has no password or hash.
- Acceptance criteria: listed tests pass.
- Status: Not Started.

#### TASK-022 NR-13 tests: password unchanged, deactivated stays blocked, unlock versus failure race
- Description: Integration tests completing the unlock scenarios: (a) after `unlock-user` the correct password logs in (AC-16, P-14); (b) password hash identical before and after unlock on a not-locked account (AC-17); (c) a deactivated and locked account still cannot log in after `unlock-user` (N-20); (d) an unlock racing a concurrent failure with two real connections ends in a defined state (count and lock both cleared or the failure counted afterwards, never a lock with count 0 or the reverse).
- Priority: P1. Design-review condition NR-13.
- Dependencies: TASK-021, TASK-028.
- Expected files or components: `tests/test_unlock_integration.py`.
- Testing requirements: as described, using the C-10 code path to create accounts and a pinned clock.
- Acceptance criteria: each of (a) to (d) is a named test; every assertion is explicit, not "records the observed outcome".
- Status: Not Started.

### WS-5 Web application

#### TASK-023 C-1 App factory and web startup checks
- Description: Factory builds the Flask app, registers extensions and blueprints, runs web-only checks: database reachable, schema verified before serving, signing key present, cookie security setting and environment mode valid, debug refused outside development, department list non-empty outside tests. CSRF automatic check disabled per TASK-003 so C-2 controls order. Cookie settings HttpOnly, SameSite=Lax, Secure by `SESSION_COOKIE_SECURE`.
- Priority: P1. Web entry point.
- Dependencies: TASK-006, TASK-007, TASK-015.
- Expected files or components: `<APP_PKG>/app.py`; `tests/test_app_startup.py`.
- Testing requirements: each missing or invalid setting fails fast naming the setting; schema without the unique index fails startup; empty department list fails outside tests; debug mode refused outside development; CSRF protection is enabled in the test configuration and a test asserts this.
- Acceptance criteria: listed tests pass; no secret appears in any startup message.
- Status: Not Started.

#### TASK-024 C-3 Response headers and error handlers
- Description: Headers `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, restrictive Content-Security-Policy, `Cache-Control: no-store` on authenticated pages, re-rendered form, login and error pages, HSTS when secure mode is on. Error pages 401, 403, 404, 413 (body over 16 KB) and 500, plain, no internals, each with a login link. 401 carries no `WWW-Authenticate` header (OQ-A15, approved).
- Priority: P1. NFR-4, FR-15, D-22.
- Dependencies: TASK-023.
- Expected files or components: routes/error package; `tests/test_errors_headers.py`.
- Testing requirements: each status page has a login link and no stack trace text; 401 has no `WWW-Authenticate`; body over 16 KB gives 413; headers present on listed pages; unhandled exception gives the generic 500 page.
- Acceptance criteria: listed tests pass; error wording uses the short generic Proposal (wording `Not Found` in requirements).
- Status: Not Started.

#### TASK-025 C-2 Per-request session validation
- Description: User loader that treats a request as unauthenticated when the session is missing, the user is missing or inactive, `auth_version` differs, or the issue time is older than the maximum lifetime (checked on the server with the C-8 clock). Wrong role gives 403. Page requests redirect to login (302); submissions return 401. Remember-me not used.
- Priority: P1. NFR-1, D-16.
- Dependencies: TASK-016, TASK-023, TASK-003, TASK-005.
- Expected files or components: auth package; `tests/test_auth_session.py`.
- Testing requirements: each rejection cause on a page request (302) and a submission (401); wrong role 403; lifetime expiry with advanced clock though the cookie is present; remember-me cookie absent.
- Acceptance criteria: listed tests pass; one mechanism is used for every protected route.
- Status: Not Started.

#### TASK-026 C-2 Ordered CSRF enforcement
- Description: Explicit CSRF check run after authentication on protected routes: step 1 authentication, session validity and role (401 or 403, body not read for unauthenticated requests); step 2 CSRF (403). `POST /login` public route: CSRF only, 403, no counter change.
- Priority: P1. AC-08b, D-5.
- Dependencies: TASK-025, TASK-003.
- Expected files or components: auth package; `tests/test_auth_csrf.py`.
- Testing requirements: unauthenticated POST with and without token gives 401; authenticated without token gives 403; `POST /login` without token gives 403 and the failure counter is unchanged.
- Acceptance criteria: listed tests pass; ordering is deterministic.
- Status: Not Started.

#### TASK-027 C-2 and C-3 Login route
- Description: `GET/POST /login`: normalise username, look up user, always verify a hash (real, or a precomputed dummy hash for unknown users), identical generic message and status 200 for every failure cause, success clears and re-issues the session with user id, `auth_version` and issue time, then 303 to the Add Employee form; `next` ignored.
- Priority: P1. FR-12, FR-16, AC-11, AC-13.
- Dependencies: TASK-025, TASK-026, TASK-019.
- Expected files or components: auth and routes packages; `tests/test_login.py`.
- Testing requirements: P-10 account created by `create-user` logs in; unknown user, wrong password and inactive account give identical status and body (N-12, N-13); functional check that the dummy-hash path runs for an unknown user (no timing assertion); external `next` is ignored.
- Acceptance criteria: listed tests pass; no username is logged.
- Status: Not Started.

#### TASK-028 C-2 Lockout in login, including NR-12 and fail-closed
- Description: Wire TASK-016 into login. Failure for an existing active account calls the conditional update only when the earlier read shows the account is not locked (NR-12: no lockout write while a lock is active); a locked account is rejected with the generic message even with the correct password. Success performs the conditional reset; if it changes no row, login is rejected. If the lock read or either counter write fails, reject with the same generic message and status, log user id and error category, never grant a session. Unknown usernames create no rows.
- Priority: P1. FR-16, AC-14, D-15, NR-12.
- Dependencies: TASK-027, TASK-016.
- Expected files or components: auth package; `tests/test_login_lockout.py`.
- Testing requirements: N-14 (5th failure locks; correct password rejected within 15 minutes; works after 15 minutes with replaced clock); expired lock restarts count at 1; success resets; lock survives re-creating the app on the same file; attempts while locked neither count nor extend the lock; a test asserts that no write statement is issued for an account that is already locked; locked case has identical status and body; unknown username creates no rows (E-16).
- Acceptance criteria: listed tests pass; the skip-write behaviour is demonstrated by a test, not asserted by comment.
- Status: Not Started.

#### TASK-029 C-2 Logout
- Description: `POST /logout`, authenticated and CSRF checked; atomically increments `auth_version` and clears the session; redirect to login. `GET /logout` does nothing. Stale or unauthenticated logout POST returns 401 with no increment.
- Priority: P1. FR-14, AC-15.
- Dependencies: TASK-026, TASK-016, TASK-027.
- Expected files or components: auth and routes packages; `tests/test_logout.py`.
- Testing requirements: P-11 logout ends the session and the old cookie is rejected afterwards; N-16 missing token gives 403, `GET` does not log out; stale-session logout returns 401 and `auth_version` is unchanged; logout ends other sessions of the same user (OQ-A10).
- Acceptance criteria: listed tests pass.
- Status: Not Started.

#### TASK-030 C-5 Employee service
- Description: `create_employee(raw fields, admin id)`: get today from C-8 and limits and departments from C-7, call C-4, run the pre-check, call the TASK-017 write. On integrity error roll back, re-query `email_normalized`: found gives the email-in-use error, otherwise a generic failure. Busy timeout or storage failure gives the generic failure. Logs employee id and admin id, validation failure counts without values.
- Priority: P1. FR-5, FR-8, FR-13, FR-17, NFR-4.
- Dependencies: TASK-012, TASK-017, TASK-005, TASK-006, TASK-007.
- Expected files or components: `<APP_PKG>/services/employee.py`; `tests/test_employee_service.py`.
- Testing requirements: valid creation; invalid input writes nothing and no audit row (N-11); duplicate and case-only duplicate (AC-05, AC-05b); resubmission shows the duplicate error (N-19); injected storage error gives generic failure.
- Acceptance criteria: listed tests pass; the service never calls the database outside C-6.
- Status: Not Started.

#### TASK-031 C-3 Add Employee routes with Post/Redirect/Get
- Description: `GET /employees/new` and `POST /employees/new`. Invalid: 200 with every error and entered values. Success: 303 to the GET with one-time success message and cleared form. Failure: generic 500 page. Authentication and CSRF order from TASK-026.
- Priority: P1. FR-1, FR-9, FR-10, AC-01, AC-09.
- Dependencies: TASK-026, TASK-030, TASK-032.
- Expected files or components: routes package; `tests/test_employee_routes.py`.
- Testing requirements: P-1, P-8 (303, empty form, message after redirect), invalid forms keep values, department outside list rejected, body over 16 KB gives 413.
- Acceptance criteria: listed tests pass; routes contain no SQL and no business rule.
- Status: Not Started.

#### TASK-032 C-9 Templates and static assets
- Description: Login page, Add Employee page (seven fields, department `<select>`, per-field error text, success area, CSRF hidden field), logout form with token, error pages with login link. Autoescape on. Plain HTML5 and CSS. Optional submit-disable script is a same-origin static file and the page works without it.
- Priority: P1. FR-2, FR-11, NFR-5.
- Dependencies: TASK-023.
- Expected files or components: `<APP_PKG>/templates/`, `<APP_PKG>/static/`; `tests/test_templates.py`.
- Testing requirements: rendered form has seven fields and the dropdown with a test department list; markup escapes user input (script text); no inline script.
- Acceptance criteria: listed tests pass; the page works with no script.
- Status: Not Started.

### WS-6 Cross-cutting tests

#### TASK-033 Mandatory lockout concurrency test
- Description: Several real connections to a temporary file database submit failures for one account concurrently; assert no lost increments, the lock set exactly once, evaluated guesses beyond 5 not exceeding the number of concurrent requests, and a correct-password attempt racing the 5th failure obtains no session after the lock exists.
- Priority: P1. Design-review requirement (NR-03).
- Dependencies: TASK-028.
- Expected files or components: `tests/test_lockout_concurrency.py`.
- Testing requirements: as stated, using threads or processes with real connections, not in-memory.
- Acceptance criteria: all assertions explicit and passing; test is deterministic enough to run in the normal suite (no unseeded sleeps as the only synchronisation).
- Status: Not Started.

#### TASK-034 Fail-closed lockout tests
- Description: Inject a failure into the counter write on the failure path and on the success path, and into the lock read; assert a generic rejection with the same status and body, no session, and an error log with user id and category but no username.
- Priority: P1. Design-review requirement (NR-03).
- Dependencies: TASK-028.
- Expected files or components: `tests/test_lockout_fail_closed.py`.
- Testing requirements: three injection points plus log capture.
- Acceptance criteria: listed assertions pass; a login is never granted without a successful success-reset write.
- Status: Not Started.

#### TASK-035 Duplicate-email race test with a defined outcome (NR-14, E-8)
- Description: Two real connections to a temporary file database with the pre-check bypassed so both insert; exactly one row; the loser must see the email-in-use error (D-25 intent). The other outcome (generic failure) fails the test and is reported as a defect to investigate. A second test confirms a non-email integrity error returns the generic failure. If TASK-004 shows the architecture's expectation cannot hold, report to the orchestrator instead of loosening the test.
- Priority: P1. Mandatory test, design-review NR-14.
- Dependencies: TASK-030, TASK-017, TASK-004.
- Expected files or components: `tests/test_duplicate_race.py`.
- Testing requirements: as stated.
- Acceptance criteria: the test asserts one named outcome; exactly one employee row and one audit row remain.
- Status: Not Started.

#### TASK-036 Atomicity and graceful storage failure tests (E-14, N-9)
- Description: Inject failure into the audit insert and into the commit; assert no Employee row remains, the response is the generic 500 page without internals, and a failed busy wait gives the generic page.
- Priority: P1. D-7, NFR-4.
- Dependencies: TASK-030.
- Expected files or components: `tests/test_atomicity.py`.
- Testing requirements: as stated.
- Acceptance criteria: row counts for Employee and AuditRecord unchanged after each injection; page has no stack trace text.
- Status: Not Started.

#### TASK-037 Authentication and CSRF integration tests (AC-08, AC-08b, NFR-1)
- Description: Unauthenticated GET gives 302 to login (N-7); unauthenticated POST with and without CSRF token gives 401 and counts unchanged (N-8); wrong role 403; authenticated POST with missing CSRF token 403 and no record; expired session then submit gives 401 (E-12); after logout a direct submission gives 401 or 403 (N-15).
- Priority: P1. NFR-1.
- Dependencies: TASK-031, TASK-029.
- Expected files or components: `tests/test_auth_integration.py`.
- Testing requirements: as stated.
- Acceptance criteria: Employee and AuditRecord counts unchanged in every rejected case.
- Status: Not Started.

#### TASK-038 End-to-end acceptance tests AC-01 to AC-10
- Description: Full path with a user created through the C-10 code path and a test department list: P-1 to P-9, P-12, P-13, N-1 to N-6, N-10, N-18, N-19, AC-05b, AC-06b, AC-07b, one audit row on success and none on any rejection (N-11), form values retained on error.
- Priority: P1. Covers FR-1 to FR-11, FR-13, FR-15, FR-17.
- Dependencies: TASK-031.
- Expected files or components: `tests/test_e2e_add_employee.py`; form factory in `tests/conftest.py`.
- Testing requirements: factory builds a valid form dictionary and each case overrides one field.
- Acceptance criteria: each AC id appears in a test name or docstring; all pass; no real personal data in fixtures.
- Status: Not Started.

#### TASK-039 Security tests
- Description: Log capture during login, failed login, lockout, account creation and a provoked storage error with a known email: no password, hash, attempted username or employee value (if present, add a logging filter per architecture 8.7); cookie flags; response headers on authenticated pages, failed re-render, login page, and 401, 403, 413 pages; debug refused outside development; error pages without stack text.
- Priority: P1. NFR-2, NFR-4, D-21, D-22.
- Dependencies: TASK-024, TASK-031, TASK-028.
- Expected files or components: `tests/test_security.py`.
- Testing requirements: as stated.
- Acceptance criteria: all listed assertions pass.
- Status: Not Started.

#### TASK-040 Account and session scenario tests AC-11 to AC-15
- Description: Deactivated account rejected at login (N-12) and an already-open session of it rejected on its next request (AC-12); one generic message for all causes (AC-13); logout flows (AC-15); session lifetime expiry; no remember-me cookie.
- Priority: P1. FR-12, FR-14, FR-16.
- Dependencies: TASK-029, TASK-028, TASK-020.
- Expected files or components: `tests/test_account_scenarios.py`.
- Testing requirements: as stated.
- Acceptance criteria: all listed tests pass.
- Status: Not Started.

### WS-7 Operations, packaging and final checks

#### TASK-041 NR-13 amendment request and test traceability
- Description: Prepare a request, through the orchestrator, for the architecture owner to update `docs/architecture.md` (not edited by this plan) so that section 2 maps FR-18 to C-10, C-6, C-8; AC-16, AC-17, P-14, P-15, N-20, E-18 to the 9.3 tests; cites OQ-19; marks the unknown-username behaviour as an approved Proposal; and replaces the stale "requirements update pending" statements. In `tests/`, name or tag each test with the ids it covers so the mapping is checkable.
- Priority: P2. Traceability and governance; does not block code.
- Dependencies: none.
- Expected files or components: request text returned to the orchestrator; test-id naming convention in `tests/conftest.py` or test docstrings.
- Testing requirements: a check (script or test) that lists FR-18, AC-16, AC-17, P-14, P-15, N-20 and E-18 and the tests that reference them.
- Acceptance criteria: the request is delivered; every listed id is referenced by at least one test (E-18 by TASK-021).
- Status: Blocked (architecture amendment needs human approval).

#### TASK-042 NR-14 WAL operational notes
- Description: Write operator notes covering: journal mode choice finalised after the deployment target is known; write-begin ordering (D-25) stands without WAL; behaviour on a network file system; ownership of the database, `-wal` and `-shm` files when the web service and operator commands run as different accounts (8.8); backups carry the same restrictions (policy `Not Found`).
- Priority: P2. Operational risk, design-review NR-14.
- Dependencies: TASK-004.
- Expected files or components: operator notes document (file name Proposal: `docs/ops-notes.md`); TASK-001 may change the location.
- Testing requirements: the TASK-004 results are referenced; a test confirms the journal mode setting in use.
- Acceptance criteria: notes address each listed point; unknown items are written exactly `Not Found`; notes contain no secret.
- Status: Not Started (final journal-mode decision depends on OQ-A3, section 8).

#### TASK-043 NR-15 operator action logging
- Description: Each operator command logs one line with the command name and the affected user id (and an outcome category), through TASK-007. No username, password, hash or database credentials. For an unknown username the line carries no username. Nothing new is stored durably (NR-15 is Noted; durable accountability is a future requirement).
- Priority: P2. Supports accountability for lock removal; no approved requirement demands more.
- Dependencies: TASK-019, TASK-020, TASK-021, TASK-007.
- Expected files or components: commands package; `tests/test_cmd_logging.py`.
- Testing requirements: log capture for each command success and failure contains command name and id only; unknown-username and weak-password cases contain no username or password.
- Acceptance criteria: listed assertions pass.
- Status: Not Started.

#### TASK-044 Configure the real department list
- Description: Provide the real department names to the web configuration and add them to deployment settings. Names are `Not Found`; no names are invented. Until supplied, tests use labelled test fixtures and the web app refuses an empty list outside tests.
- Priority: P1. The web app cannot start with real configuration without names (OQ-2).
- Dependencies: TASK-023; user input DEC-3.
- Expected files or components: settings file (non-secret).
- Testing requirements: startup test with the supplied list; dropdown shows exactly the supplied names.
- Acceptance criteria: list supplied by the user and recorded in the settings; test passes.
- Status: Blocked (OQ-2).

#### TASK-045 Production serving and deployment packaging
- Description: Choose and document the production WSGI server, HTTPS termination, and the file-ownership setup of 8.8. Windows-native option (for example waitress) was named only as an example in the architecture. Do not choose before the deployment target is known.
- Priority: P2. Needed for release, not for development.
- Dependencies: TASK-023, TASK-042; user input DEC-4.
- Expected files or components: deployment notes; server entry point (names `Not Found`).
- Testing requirements: smoke start through the chosen server; secure-cookie setting on; debug refused.
- Acceptance criteria: target and server recorded by the user; startup checks pass through that server.
- Status: Blocked (OQ-A3).

#### TASK-046 Manual browser smoke check (NFR-5)
- Description: Manual check of the login, add-employee and logout flows on current desktop Chrome, Edge, Firefox and Safari; results recorded in verification, not claimed here.
- Priority: P2. NFR-5; no automated cross-browser tooling is designed.
- Dependencies: TASK-038, TASK-032.
- Expected files or components: checklist recorded in verification output.
- Testing requirements: manual.
- Acceptance criteria: a result (pass or defect) for each of the four browsers is recorded; none is pre-filled.
- Status: Not Started.

#### TASK-047 Performance smoke test (NFR-3)
- Description: A single submission completes well within 3 seconds on the test machine. Informative only; not a pass or fail gate; no load test until OQ-12 is answered.
- Priority: P3. Conditions `Not Found`.
- Dependencies: TASK-038.
- Expected files or components: `tests/test_perf_smoke.py`.
- Testing requirements: one timed submission; slow-request log entry when over 3 seconds.
- Acceptance criteria: test exists, marked informative; its failure does not block release.
- Status: Not Started.

#### TASK-048 Final verification and traceability check
- Description: Run the full pytest suite; check every FR, NFR and AC id in section 6 has passing tests; check no secret in any file; check `git status` shows only intended files and branch `feature/doc-sync-claude`; list outstanding blocked tasks and `Not Found` items. No commit unless the orchestrator instructs.
- Priority: P1. Release gate.
- Dependencies: TASK-022, TASK-033 to TASK-040, TASK-042, TASK-043.
- Expected files or components: verification output (location by the orchestrator).
- Testing requirements: full suite, plus a secret scan of tracked files.
- Acceptance criteria: suite exits 0 (reported from a real run, not predicted); all ids in section 6 have at least one passing test; remaining blockers listed.
- Status: Not Started.

## 5. Dependency Mapping

Direct dependencies (no cycles; every id exists):

| Task | Depends on | | Task | Depends on |
|---|---|---|---|---|
| 001 | none | | 025 | 003, 005, 016, 023 |
| 002 | 001 | | 026 | 003, 025 |
| 003 | 002 | | 027 | 019, 025, 026 |
| 004 | 002 | | 028 | 016, 027 |
| 005 | 002 | | 029 | 016, 026, 027 |
| 006 | 002 | | 030 | 005, 006, 007, 012, 017 |
| 007 | 002 | | 031 | 026, 030, 032 |
| 008 | 002 | | 032 | 023 |
| 009 | 008 | | 033 | 028 |
| 010 | 008 | | 034 | 028 |
| 011 | 008 | | 035 | 004, 017, 030 |
| 012 | 009, 010, 011 | | 036 | 030 |
| 013 | 002 | | 037 | 029, 031 |
| 014 | 002, 004, 006 | | 038 | 031 |
| 015 | 014 | | 039 | 024, 028, 031 |
| 016 | 005, 014 | | 040 | 020, 028, 029 |
| 017 | 004, 014 | | 041 | none |
| 018 | 006, 007, 014, 015 | | 042 | 004 |
| 019 | 013, 018 | | 043 | 007, 019, 020, 021 |
| 020 | 016, 018 | | 044 | 023, DEC-3 |
| 021 | 016, 018 | | 045 | 023, 042, DEC-4 |
| 022 | 021, 028 | | 046 | 032, 038 |
| 023 | 006, 007, 015 | | 047 | 038 |
| 024 | 023 | | 048 | 022, 033 to 040, 042, 043 |

Critical path: 001, 002, 004, 014, 015, 018, 019, 027, 028, 029, 026 chain, 031, 038, 048.

## 6. Requirements and Architecture Traceability

| Requirement | Tasks |
|---|---|
| FR-1, AC-01, AC-08, AC-08b, NFR-1 | 025, 026, 031, 037 |
| FR-2, FR-11, AC-01, P-7 | 011, 032, 038 |
| FR-3, AC-03 | 008, 012, 038 |
| FR-4, AC-04 | 009, 038 |
| FR-5, AC-05, AC-05b | 009, 014, 017, 030, 035, 038 |
| FR-6, AC-06, AC-06b | 010, 038 |
| FR-7, AC-07, AC-07b | 005, 011, 038 |
| FR-8, AC-02 | 017, 030, 038 |
| FR-9, AC-09 | 031, 032, 038 |
| FR-10, N-10 | 012, 031, 038 |
| FR-12, AC-11, AC-12 | 018, 019, 020, 027, 040 |
| FR-13, AC-10, N-11 | 014, 017, 030, 038 |
| FR-14, AC-15 | 026, 029, 032, 040 |
| FR-15, N-18, E-17 | 006, 008, 009, 024, 031 |
| FR-16, AC-13, AC-14 | 013, 016, 027, 028, 033, 034 |
| FR-17, N-19 | 030, 038 |
| FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18 | 016, 021, 022, 041 |
| NFR-2 | 025, 039, 042, deployment constraints in 045 |
| NFR-3 | 047 (informative) |
| NFR-4, N-9, E-14 | 024, 030, 036, 039 |
| NFR-5 | 032, 046 |
| E-8 | 017, 035 |
| E-9, E-15 | 030, 031, 038 |
| E-12 | 025, 037 |
| E-16 | 028 |
| E-10, E-13 | no task (unmapped, behaviour `Not Found`) |

Architecture coverage: C-1 (023), C-2 (025 to 029), C-3 (024, 027, 029, 031), C-4 (008 to 013), C-5 (030), C-6 (014 to 017), C-7 (006), C-8 (005), C-9 (032), C-10 (018 to 021), C-11 (007, 043). Decisions: D-5 (026), D-7 (017, 036), D-15 (016, 028, 033, 034), D-16 (025, 029), D-17 (027), D-18 (027), D-19 (014, 015), D-20 (030, 035), D-21 (004, 039), D-22 (024, 039), D-23 (014), D-24 (018, 023), D-25 (004, 017, 030, 035, 042).

## 7. Implementation Sequence

1. TASK-001 (user decision), then TASK-002.
2. Verification and foundations: 003, 004, 005, 006, 007, 008, 013.
3. Pure rules: 009, 010, 011, then 012.
4. Persistence: 014, then 015, 016, 017.
5. Commands: 018, then 019, 020, 021.
6. Web: 023, then 024, 032 and 025, then 026, 027, then 028, 029; 030; 031.
7. Tests and unlock integration: 022, 033 to 040.
8. Operations and governance: 041 (any time), 042, 043, 044 and 045 when unblocked, 046, 047.
9. Final: 048.

### 7.1 Parallelizable task groups
- PG-1 after TASK-002: 003, 004, 005, 006, 007, 008, 013.
- PG-2 after TASK-008: 009, 010, 011.
- PG-3 after TASK-014: 015, 016, 017 (016 also needs 005; 017 needs 004).
- PG-4 after TASK-018: 019, 020, 021 (020, 021 need 016; 019 needs 013).
- PG-5 after TASK-023: 024 and 032.
- PG-6 after TASK-028: 033 and 034 (parallel with 029).
- PG-7 after TASK-030: 035 and 036.
- PG-8 after TASK-038: 046 and 047.
- TASK-041 is independent of all others.
- Command tasks (WS-4) and pure-rule tasks (WS-2) can run in parallel with web setup (023) once their prerequisites are done.

## 8. Blocked Tasks and Decisions

### 8.1 Blocked tasks

| Task | Blocking dependency or decision | Reason | Required resolution |
|---|---|---|---|
| TASK-001 | DEC-1 user decision | `CLAUDE.md` describes a CLI and `src/doc_sync/`; the architecture fixes no package layout (DR-24) | User answers (a), (b), (c); orchestrator records it |
| TASK-041 | DEC-2 architecture owner and human approval | The architecture may not be edited without approval | Human approval of the NR-13 amendment |
| TASK-044 | DEC-3 / OQ-2 | Department names `Not Found` | User supplies names |
| TASK-045 | DEC-4 / OQ-A3 | Deployment target and platform `Not Found` | User names the target |

Partially blocked: TASK-042 (notes can start; final journal-mode choice waits for OQ-A3). Transitively gated: every task except TASK-041 waits on TASK-001 through TASK-002. Direct blocked count: 4 (plus 1 partial).

### 8.2 Decisions needing human approval

| Id | Decision | Source |
|---|---|---|
| DEC-1 | Update `CLAUDE.md` or not; Flask package location and name; `tests/` layout. No silent edit. | DR-24, TASK-001 |
| DEC-2 | Approve the NR-13 architecture amendment (traceability and tests for FR-18 and related ids, remove "pending" statements) | NR-13 |
| DEC-3 | Provide department names | OQ-2 |
| DEC-4 | Deployment target, platform, WSGI server, journal mode final choice | OQ-A3, NR-14 |
| DEC-5 | Confirm the user approval covers delegated defaults and FR-18 as recorded (written sign-off `Not Found`) | NR-09 |
| DEC-6 | Approve this plan before development starts | rule: human approval required |

### 8.3 Items that stay `Not Found` (configurable or unplanned, never invented)

| Item | Handling |
|---|---|
| Department names (OQ-2) | Empty configuration; test fixtures only; TASK-044 blocked |
| Allowed characters in names and job title; job title list vs free text (OQ-11) | No restriction applied; documented in TASK-008 |
| Normal operating conditions (OQ-12) | Informative smoke test only (TASK-047) |
| Roles other than HR Administrator (OQ-16) | Not designed; only `hr_administrator` |
| Audit retention, format, viewing (OQ-18) | Rows written only; no screen |
| Deployment target (OQ-A3), backup policy | TASK-045 blocked; TASK-042 notes say `Not Found` |
| Password reset, reactivation, forgotten password (OQ-17, OQ-19) | Not planned |
| Session timeout as a business rule; other password rules (OQ-15) | Technical 8-hour lifetime only; password min 12 |
| Wording of validation and server error messages | Short generic Proposal |
| Vulnerability scanning | Not planned |

## 9. Testing Activities

| Level | Tasks | Scope |
|---|---|---|
| Unit (no Flask, no database) | 005, 006, 008 to 013 | All field rules, boundaries, Unicode, injected date, configuration |
| Library characterization | 003, 004 | CSRF, hooks, token lifetime, remember-me, hidden parameters, write-begin, WAL, no-row update lock |
| Persistence | 014 to 017 | Schema, indexes, conditional updates, atomic write |
| Command (Click runner) | 018 to 022, 043 | Prompts only, environment ignored, idempotency, unknown username, logging |
| Integration (Flask test client, temporary file database) | 023 to 032, 037, 038, 040 | AC-01 to AC-17 paths, CSRF enabled |
| Concurrency (real connections) | 033, 035, 022(d) | Lockout, duplicate race, unlock race |
| Fault injection | 034, 036 | Fail closed; audit and commit failure |
| Security | 039 | Log redaction, flags, headers, debug refusal |
| Manual | 046 | Four desktop browsers |
| Informative | 047 | NFR-3 smoke |

Positive and negative scenarios from requirements sections 6 and 7 are assigned in tasks 038, 040, 027 to 029. Regression: the whole suite runs in TASK-048. No result is claimed in this plan.

## 10. Risks and Mitigations

| Risk | Mitigation | Task |
|---|---|---|
| Layout and `CLAUDE.md` conflict cause rework or wrong rules applied | Ask the user first; edit nothing silently | 001 |
| Library behaviour differs from architecture assumptions (CSRF order, WAL, write-begin) | Verify before dependent tasks; report contradictions, do not work around | 003, 004 |
| Lockout weaker or noisy under concurrency; write contention on locked accounts (NR-12) | Single conditional update, skip write when locked, mandatory concurrency and fail-closed tests | 016, 028, 033, 034 |
| Race returns generic 500 instead of duplicate message | Pre-check ends before write; test asserts the defined outcome | 017, 035 |
| Personal data in logs through exception text | Parameter hiding, log-capture test, fallback filter | 004, 039 |
| NFR-2 storage protection not enforceable by the application | Documented operator responsibility; ignore rules; notes | 002, 042 |
| Known-username lockout availability, timing difference | Accepted by the user; `unlock-user` recovery; no timing test | 021, 027 |
| Department names or deployment target unknown at release | Blocked items are visible; configuration only | 044, 045 |
| Requirements defaults are not stakeholder-specified | All values configurable via TASK-006 | 006 |
| Flaky concurrency tests | Real synchronisation, bounded assertions, no timing gates | 033, 035 |
| Dependency drift or Python 3.11 incompatibility | Pin versions and check at scaffolding | 002 |

## 11. Definition of Done

Task level: acceptance criteria met; named pytest tests exist and pass in a real run; type hints on every function signature; functions small and single-purpose with no duplicated logic; missing data written exactly `Not Found`; no secret, password, hash or personal data in code, logs, fixtures or commits; work on `feature/doc-sync-claude` only.

Release level: all non-blocked tasks complete; TASK-048 passes; every FR, NFR and AC in section 6 has a passing test (except manual and informative items, which have recorded results); blocked items listed with owners; `CLAUDE.md` handled per DEC-1.

## 12. Approval Status

- Plan status: APPROVED by the user on 2026-11-20 (DEC-6), relayed through the orchestrator. Decisions: DEC-1 resolved (TASK-001): `CLAUDE.md` rewritten for this web app by user instruction; app package is `src/employee_app/`, tests in top-level `tests/`, legacy `src/doc_sync/` untouched. DEC-2 (NR-13 architecture amendment, TASK-041), DEC-5 (approvals confirmed) accepted per orchestrator recommendation. DEC-3 department names and DEC-4 deployment target remain `Not Found` (TASK-044, TASK-045 blocked).
- Approved requirements and architecture are unchanged by this plan.
- Pipeline state: not updated by this agent (the orchestrator does that).
- Human sign-off record: Not Found
