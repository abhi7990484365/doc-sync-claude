---
description: Step 7: run verification and write verification-report.md (tester)
argument-hint: <optional notes>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Inputs: `src/`, `tests/`, `docs/requirements.md`.
2. Invoke agent `tester` -> `docs/verification-report.md` and `docs/test-output.txt`
   (cases: happy path, Not Found, missing field, empty repo, API failure mocked; plus a content
   check of the generated `PROJECT_DOC.md`).
3. If defects are found, send them to agent `developer`, then re-run the tester.
4. Commit: `test: add verification report`.
