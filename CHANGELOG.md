# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] SCRUM-101 Add a New Employee (2026-11-20)

Version number: Not Found.

### Added
- `employee_app` Flask web application: a login-protected HR form (`GET/POST /employees/new`) to add an employee with seven validated fields (field list in `docs/requirements.md`; includes email, 10-digit phone, joining date not in the past, and a department from a configured list); duplicate emails (case-insensitive) and invalid input are rejected with field errors.
- Each successful creation writes the employee and one audit record in a single transaction; rejected submissions write nothing.
- Login with account lockout after 5 failed attempts (15 minutes), logout (POST with CSRF token), CSRF protection, generic error pages and security headers.
- `employee-admin` operator commands: `init-db`, `create-user`, `deactivate-user`, `unlock-user` (also `python -m employee_app.commands`).
- Packaging (`pyproject.toml`), pinned `requirements.txt` and `requirements-dev.txt`, `pytest.ini`.
- Test suite in `tests/`: 441 passed, 0 failed, 0 skipped (Python 3.11.9, Windows).
- Pipeline documents for SCRUM-101 in `docs/` (user story, requirements, architecture, design review, plan, implementation report, code review, verification report, ops notes).

### Changed
- `CLAUDE.md` rewritten for the employee web app; `.claude/` rules, agents, skills and the pre-bash hook message now name branch `feature/doc-sync-claude` and package `employee_app`.
- `.gitignore` rewritten (`.env`, database files, `*.egg-info/`, `.venv/`); `README.md` has a "Run and install" section for the web app.

### Security
- The signing key (`EMPLOYEE_APP_SECRET_KEY`) must be at least 32 characters; credentials are read from environment variables only. A pattern search of the repository found no real credentials (no dedicated scanner was run).

### Known limitations
- Department names and deployment target: Not Found. The production app does not start until a department list is supplied.
- No lock file for transitive dependencies. Manual browser check, interactive `create-user` prompt, load and network file system runs: Not Run.

## [Unreleased] earlier doc_sync work (code not present in this tree)

The entries below describe a `doc_sync` CLI whose source (`src/doc_sync/`) does not exist in this branch; they are kept as history.

### Added
- `doc_sync` CLI (`python -m doc_sync [REPO_PATH]`, console script `doc_sync = doc_sync.cli:main`) that scans a repository and writes `docs/PROJECT_DOC.md` with seven fixed sections.
- Readers for `pyproject.toml`, `README.md`, `requirements.txt`, entry points, language detection by file extension, and the last git commit.
- Atomic, deterministic output writer; missing data is written as `Not Found`.
- Test suite: 257 tests (253 passed, 4 skipped on Windows, 0 failed).
- Agentic SDLC pipeline files (`.claude/` agents, commands, hooks, skill) and pipeline documents in `docs/`.

### Changed
- `.gitignore` reduced; `README.md` updated.

### Fixed
- Headings injected through the Name, HTML, blockquote or list content can no longer change the document structure (CR-1, CR-2).
- Credentials and URL query tokens are stripped from dependency lines; backslash continuations are joined (CR-5, CR-6).
- Windows junctions are pruned in the repo walk; CLI errors are hardened; output file mode is preserved; an empty path is rejected (CR-3, CR-4, CR-8, CR-10).
- `find_git` and last-commit validation hardened (CR-7, CR-9).

### Security
- `pip-audit`: No known vulnerabilities found. Runtime uses the standard library only.
