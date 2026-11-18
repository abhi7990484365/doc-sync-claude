# agentic-sdlc — always-on rules

Project: a Python 3.11 CLI (`doc_sync`) that scans a repo and writes
`docs/PROJECT_DOC.md`. It is built by an agentic SDLC pipeline run with `/sdlc`.

## Code rules
- Python 3.11, type hints on every function signature.
- Tests with pytest in `tests/`; every new behaviour gets a test.
- Small, single-purpose functions. No duplicated logic: extract a shared helper.
- Missing data is written as exactly `Not Found` (case and spacing exact).
- Handle API failures, missing files and empty repos without crashing.
- Never print or log secrets. Credentials come only from environment variables.
- Never write tokens or passwords into any file, commit, log or PR.

## Git rules
- Work only on branch `feature/doc-sync`. Never commit to or push to `main`.
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
- Output format of `PROJECT_DOC.md` is defined in `.claude/skills/doc-sync-format/SKILL.md`.

## Layout
- `src/doc_sync/` code, `tests/` tests, `docs/` pipeline artefacts.
- `.claude/agents/` subagents, `.claude/commands/` slash commands,
  `.claude/skills/` skills, `.claude/hooks/` hook scripts, `.mcp.json` MCP servers.
