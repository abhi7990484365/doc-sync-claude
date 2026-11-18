---
description: Step 1: turn a user story into docs/requirements.md (analyst)
argument-hint: <Confluence link/ID or pasted story; blank = reuse docs/user-story.md>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Get the story: Confluence link/ID via the atlassian MCP, pasted text, or the existing
   `docs/user-story.md` if no argument. Save it to `docs/user-story.md`.
2. Invoke agent `analyst` (input `docs/user-story.md` plus any answers) -> `docs/requirements.md`.
3. GATE 1: if it returns QUESTIONS, ask me at most 5 per round, wait, re-invoke the analyst
   with my answers. Repeat until I say "finalize".
4. Commit: `docs: add requirements`.
