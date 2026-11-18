---
description: Step 4: create the dependency-ordered docs/impl-plan.md (planner)
argument-hint: <optional notes>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Inputs: `docs/architecture.md` and `docs/design-review.md`.
2. Invoke agent `planner` -> `docs/impl-plan.md` (ID, Task, Files, Requirements, Blocked by, Status).
3. Check every FR-/NFR- id is covered by a task.
4. GATE 3: show me the plan and wait for approval (skipped only if I said "auto").
5. Commit: `docs: add implementation plan`.
