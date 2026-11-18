---
description: Step 5: implement tasks from impl-plan.md one at a time (developer)
argument-hint: <optional task id, e.g. T3; blank = all pending>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Input: `docs/impl-plan.md`. Use the task id in $ARGUMENTS, else every Todo task in order.
2. For each task whose "Blocked by" tasks are Done: invoke agent `developer` with ONLY that task.
3. Confirm `python -m pytest -q` passes (real output). On failure, send it back to the developer once.
4. Mark the task Done in `impl-plan.md`, commit (`feat:` or `test:`), then go to the next task.
