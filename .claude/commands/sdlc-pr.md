---
description: Step 8: write CHANGELOG and PR description, then push and open the PR (pr-writer)
argument-hint: <optional PR title>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

Run this single SDLC step as the orchestrator. First read `.claude/sdlc-common.md` and
follow its rules. Extra input from me (optional): $ARGUMENTS

## Procedure
1. Inputs: all of `docs/`, `docs/test-output.txt`, git history.
2. Invoke agent `pr-writer` -> `CHANGELOG.md` and `docs/pr-description.md` with EXACTLY these
   sections: Summary, Changes Made, Test Evidence, Known Limitations, Reviewer Checklist.
3. GATE 4: show me the PR title and description; wait for approval.
4. Commit: `docs: add changelog and PR description`. Then `git push -u origin feature/doc-sync` and
   call the GitHub MCP `create_pull_request` (base `main`, head `feature/doc-sync`) with
   `docs/pr-description.md` as the body. Print the PR URL.
