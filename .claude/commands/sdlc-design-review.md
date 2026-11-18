---
description: Step 3: review architecture.md and record decisions (reviewer + architect)
argument-hint: <optional: auto>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Input: `docs/architecture.md`, `docs/requirements.md`.
2. Invoke agent `reviewer` (read-only). Write its findings to `docs/design-review.md` with a
   Decision column.
3. GATE 2: ask me Accept/Reject/Defer per finding (skipped only if I said "auto").
4. Invoke agent `architect` with the accepted findings to update `docs/architecture.md`.
5. Commit: `docs: add design review`.
