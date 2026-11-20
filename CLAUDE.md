# agentic-sdlc — always-on rules

Project: SCRUM-101 "Add a New Employee" — a Python 3.11 web app (Flask) where an
authenticated HR Administrator adds employees through a browser form, plus operator
CLI commands (`init-db`, `create-user`, `deactivate-user`, `unlock-user`). It is built
by an agentic SDLC pipeline run with `/sdlc`. Approved specs: `docs/requirements.md`,
`docs/architecture.md`, `docs/design-review.md`, `docs/impl-plan.md`.
The earlier `doc_sync` CLI (`src/doc_sync/`) is legacy code left untouched; do not
modify or delete it unless the user asks.

## Code rules
- Python 3.11, type hints on every function signature.
- Tests with pytest in `tests/`; every new behaviour gets a test.
- Small, single-purpose functions. No duplicated logic: extract a shared helper.
- Missing data is written as exactly `Not Found` (case and spacing exact).
- Handle invalid input, database errors and server errors gracefully (no tracebacks to users).
- Never print or log secrets. Credentials come only from environment variables.
- Never write tokens or passwords into any file, commit, log or PR.

## Git rules
- Work only on branch `feature/doc-sync-claude`. Never commit to or push to `main`.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`).
- Never force-push.

## Pipeline rules
- Orchestrator is the main session running `/sdlc` (`.claude/commands/sdlc.md`).
  Subagents cannot start subagents or talk to the user.
- Each step has its own command `.claude/commands/sdlc-*.md`; `/sdlc` runs them in order.
  Shared orchestrator rules: `.claude/sdlc-common.md`.
- Each step reads one named input file and writes one named output file in `docs/`.
- Never invent facts, requirement ids, or test results. Unknown = `Not Found`.
- Pipeline state lives in `docs/sdlc-state.md` so a new session can resume.

## Layout
- `src/employee_app/` web app code, `tests/` tests, `docs/` pipeline artefacts.
- `src/doc_sync/` legacy CLI (untouched).
- `.claude/agents/` subagents, `.claude/commands/` slash commands,
  `.claude/skills/` skills, `.claude/hooks/` hook scripts, `.mcp.json` MCP servers.
