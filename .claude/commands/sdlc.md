---
description: Run the full agentic SDLC for a user story and open a GitHub PR
argument-hint: <Confluence link/ID or pasted user story>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

You are the ORCHESTRATOR. Read `.claude/sdlc-common.md` and follow it for every step.
Input: $ARGUMENTS

## Setup
1. If `docs/sdlc-state.md` exists, show it and ask me: resume from the recorded step, or restart.
2. Check the atlassian and github MCP servers are available; if one is not, tell me and ask
   me to paste the input instead (github is only needed at step 8).

## Pipeline
Run each step by following its command file exactly, in order. Each file defines the agent,
input, output, gate and commit message. Pass $ARGUMENTS to step 1 only.

| # | Step | Procedure file | Agent | Output |
|---|------|----------------|-------|--------|
| 1 | Requirements | `.claude/commands/sdlc-requirements.md` | analyst | docs/requirements.md |
| 2 | Architecture | `.claude/commands/sdlc-architecture.md` | architect | docs/architecture.md |
| 3 | Design review | `.claude/commands/sdlc-design-review.md` | reviewer, architect | docs/design-review.md |
| 4 | Plan | `.claude/commands/sdlc-plan.md` | planner | docs/impl-plan.md |
| 5 | Implement | `.claude/commands/sdlc-implement.md` | developer | src/, tests/ |
| 6 | Code review | `.claude/commands/sdlc-code-review.md` | reviewer, developer | docs/code-review.md |
| 7 | Verify | `.claude/commands/sdlc-verify.md` | tester | docs/verification-report.md, docs/test-output.txt |
| 8 | PR | `.claude/commands/sdlc-pr.md` | pr-writer | CHANGELOG.md, docs/pr-description.md, the PR |

## Gates (stop and wait)
(1) clarifying questions and my "finalize", (2) design-review decisions Accept/Reject/Defer,
(3) approval of impl-plan.md, (4) approval of the PR title/description before push.
If I say "auto", skip gates 2 and 3 only; gates 1 and 4 always apply.

## Re-running a single step
I can also run any step alone with its `/sdlc-*` command. If I change an earlier output, tell me
which later steps are now stale instead of silently re-running them.
