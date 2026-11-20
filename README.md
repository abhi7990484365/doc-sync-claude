# agentic-sdlc
Claude Code pipeline that turns a user story into a GitHub PR (use case: Automated Documentation Sync).
1. Install Python 3.11, then `pip install -r requirements-dev.txt`.
2. Create a GitHub fine-grained PAT for this repo only: Contents and Pull requests read/write.
3. `export GITHUB_PAT=<your token>` (never commit it).
4. Start Claude Code in this folder: `claude`.
5. Run `/mcp` and authenticate `atlassian`; check `github` is connected.
6. Run `/sdlc <Confluence link or pasted user story>`.
7. Answer the analyst's questions, then say `finalize`.
8. Approve design-review decisions, the impl plan and the PR text at each gate (`auto` skips gates 2-3).
9. The PR URL is printed at the end; progress is in `docs/sdlc-state.md`.
10. Run tests anytime with `python -m pytest -q`.

Single steps: `/sdlc-requirements`, `/sdlc-architecture`, `/sdlc-design-review`, `/sdlc-plan`, `/sdlc-implement`, `/sdlc-code-review`, `/sdlc-verify`, `/sdlc-pr`.

## Run and install (Add a New Employee web app)

Requires Python 3.11.

- Install the app and operator commands: `pip install -e .` (runtime pins are also in `requirements.txt`). Test and audit tools: `pip install -r requirements-dev.txt` (pins `pytest` and `pip-audit`). Check runtime dependencies: `pip-audit -r requirements.txt`.
- Environment variables (names only; set the values yourself, never commit them):
  - `EMPLOYEE_APP_DB_PATH` (needed by every command and the web app)
  - `EMPLOYEE_APP_SECRET_KEY` (web app only; at least 32 characters)
  - `EMPLOYEE_APP_ENV` (web app only: `development`, `production` or `testing`)
  - `EMPLOYEE_APP_COOKIE_SECURE` (optional, default on; set to `0` only for local development over HTTP)
  - `EMPLOYEE_APP_SETTINGS_FILE` (optional JSON file of non-secret settings, for example the `departments` list; the web app refuses an empty department list outside `testing`)
- Create the database: `employee-admin init-db`
- Create an HR Administrator (prompts for username and a hidden password, twice; interactive terminal only): `employee-admin create-user`
- Other operator commands: `employee-admin deactivate-user USERNAME`, `employee-admin unlock-user USERNAME`. Also available as `python -m employee_app.commands`.
- Start the web app (development server only): `flask --app employee_app.app:create_app run`, then open `/login`. A production server is not chosen yet.
- Run the tests: `python -m pytest -q`
