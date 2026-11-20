# Operator Notes: SCRUM-101 Add a New Employee (TASK-042, NR-14)

Unknown items are written exactly `Not Found`. No secret appears in this file.

## 1. SQLite journal mode

- The engine switches every connection to write-ahead journal mode (`PRAGMA journal_mode=WAL`) and enables foreign keys (`src/employee_app/db/engine.py`). A test asserts the mode in use (`tests/test_db_schema.py::test_foreign_keys_and_wal_are_on`).
- TASK-004 results (`tests/test_lib_sqlite.py`, run on a temporary file database): WAL is active and a reader is not blocked by an open writer; a write transaction that begins as `BEGIN IMMEDIATE` waits for the busy wait at its beginning and then fails at its beginning; a deferred read-then-write transaction fails late under contention; an `UPDATE` that matches no row still takes the writer lock until the transaction ends.
- Final journal-mode choice: depends on the deployment target, which is `Not Found` (OQ-A3). The begin-as-write ordering (D-25) does not depend on WAL.
- Network file systems: `Not Found` (not tested). WAL is known to need shared memory between processes on one host; use a local disk until the target is known.

## 2. Files and ownership (architecture 8.8)

- The database location is the setting `EMPLOYEE_APP_DB_PATH`. Put it outside the repository and outside any served or static directory.
- With WAL, SQLite also creates `<name>-wal` and `<name>-shm` next to the database. They contain the same data and need the same protection. `.gitignore` excludes `*.db`, `*.sqlite*`, `*-wal`, `*-shm`.
- The web service and the operator commands (`python -m employee_app.commands ...`) open the same files. If they run as different accounts, both accounts need read and write access to the database file, the `-wal` and `-shm` files and the directory (SQLite creates the `-wal` and `-shm` files with the permissions of the first process that opens the database). Exact account setup: `Not Found` (platform unknown).
- The application cannot enforce or prove file permissions on every platform. NFR-2 at storage level is an operator responsibility (residual risk).

## 3. Backups

Backups must carry the same restrictions as the live files and must include the `-wal` file or be taken through SQLite's backup mechanism. Backup policy: `Not Found`.

## 4. Operator commands

- `python -m employee_app.commands init-db` creates and verifies the schema (needs only `EMPLOYEE_APP_DB_PATH`).
- `create-user` prompts for the username and for the password (hidden, twice). `deactivate-user USERNAME` and `unlock-user USERNAME` take the username as an argument.
- Each command logs one line with the command name, an outcome category and (when known) the user id. No username, password or hash is logged (NR-15). Nothing is stored durably about operator actions; durable accountability is a future requirement.

## 5. Configuration names (Proposal, TASK-006)

`EMPLOYEE_APP_DB_PATH`, `EMPLOYEE_APP_SECRET_KEY` (signing key, environment only), `EMPLOYEE_APP_COOKIE_SECURE` (default on), `EMPLOYEE_APP_ENV` (`development`, `production` or `testing`), `EMPLOYEE_APP_SETTINGS_FILE` (optional JSON with non-secret settings: `departments`, limits, lockout, session lifetime, ...). Department names: `Not Found` (list is empty by default; the web app refuses an empty list outside `testing`). Production WSGI server and HTTPS termination: `Not Found` (TASK-045 blocked).

## 6. Strict referer check over HTTPS (finding from TASK-003)

When the app sees an HTTPS request (for example through a trusted proxy that forwards the scheme), Flask-WTF also requires a same-origin `Referer` header on POST requests (`WTF_CSRF_SSL_STRICT`, on by default). Browsers send it for same-origin form posts; a proxy or policy that strips it would make every POST fail with 403. Verify this on the real deployment target.
