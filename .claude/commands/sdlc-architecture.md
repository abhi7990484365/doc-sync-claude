---
description: Step 2: design the architecture from requirements.md (architect)
argument-hint: <optional notes>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Input: `docs/requirements.md`.
2. Invoke agent `architect` -> `docs/architecture.md` (Components, Mermaid Diagram, Data Flow,
   Technology Choices, Error Handling, Requirement Traceability).
3. Check every FR-/NFR- id appears in the traceability table.
4. Commit: `docs: add architecture`.
