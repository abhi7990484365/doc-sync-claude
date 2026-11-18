---
description: Step 6: review src/ and tests/ against the checklist, then fix accepted issues (reviewer + developer)
argument-hint: <optional notes>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Run `pip-audit -r requirements.txt`; keep the real output (if it cannot run, record `Not Found`).
2. Invoke agent `reviewer` with `src/`, `tests/`, `docs/requirements.md` and the pip-audit output.
   Checklist: Correctness, Security, Error Handling, Test Coverage, Code Clarity, DRY, Dependency Safety.
3. Write `docs/code-review.md` (findings, verdict per area, Decision column).
4. Ask me which findings to accept. Invoke agent `developer` to fix only those; confirm pytest passes.
5. Commit: `docs: add code review` and `fix: ...` for the fixes.
