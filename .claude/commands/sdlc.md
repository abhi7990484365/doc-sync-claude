---
description: Run the full agentic SDLC for a user story and open a GitHub PR
argument-hint: <Confluence link/ID or pasted user story>
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, mcp__atlassian, mcp__github
---

You are the ORCHESTRATOR. You are the main session; subagents cannot start other
subagents or talk to the user. You delegate each step to a subagent with the Task
tool, verify and commit its output file, and pass that file to the next subagent.
Follow CLAUDE.md. Input: $ARGUMENTS

## Setup
1. `git branch --show-current` must be `feature/doc-sync`; otherwise stop and tell me.
2. If `docs/sdlc-state.md` exists, show it and ask me whether to resume or restart.
3. Get the story: if $ARGUMENTS is a Confluence link/ID, read it with the atlassian MCP;
   if the tool is unavailable, tell me and ask me to paste the story. Otherwise treat
   $ARGUMENTS as the pasted story. Save it to `docs/user-story.md`.

## After EVERY step
- Verify the output file exists and has its required sections. If not, re-invoke the
  subagent once with the missing sections named; if still bad, stop and tell me.
- `git add` the output and `git commit` (Conventional Commit, e.g. `docs: add requirements`).
- Update `docs/sdlc-state.md`: current step, status, last commit sha, pending gate. Commit it with the step.

## Pipeline
1. **Requirements** — agent `analyst`, input `docs/user-story.md` -> `docs/requirements.md`.
   GATE 1: if the analyst returns QUESTIONS, ask me at most 5 per round, wait for my
   answers, re-invoke the analyst with them. Repeat until I say "finalize".
2. **Architecture** — agent `architect`, input `requirements.md` -> `docs/architecture.md`.
3. **Design review** — agent `reviewer`, input `architecture.md`. Write the findings to
   `docs/design-review.md` with a Decision column. GATE 2: ask me Accept/Reject/Defer
   per finding. Then re-invoke `architect` with the accepted findings to update `architecture.md`.
4. **Plan** — agent `planner`, inputs `architecture.md` + `design-review.md` -> `docs/impl-plan.md`.
   GATE 3: show the plan and wait for my approval.
5. **Implement** — agent `developer`, ONE task per invocation in dependency order,
   skipping Blocked tasks. After each task: confirm `python -m pytest -q` passes, mark the
   task Done in `impl-plan.md`, commit (`feat:`/`test:`).
6. **Code review** — run `pip-audit -r requirements.txt` and keep the real output. Invoke
   `reviewer` with src/, tests/, requirements.md and that output. Checklist: Correctness,
   Security, Error Handling, Test Coverage, Code Clarity, DRY, Dependency Safety. Write
   `docs/code-review.md` (finding, verdict per area, decision). Ask me which findings to
   accept, then invoke `developer` to fix the accepted ones and commit.
7. **Verify** — agent `tester` -> `docs/verification-report.md` and `docs/test-output.txt`.
   If defects are found, send them to `developer`, then re-run `tester`.
8. **PR** — agent `pr-writer`, inputs all docs + git history -> `CHANGELOG.md` and
   `docs/pr-description.md` (sections: Summary, Changes Made, Test Evidence, Known
   Limitations, Reviewer Checklist — exactly these). GATE 4: show me the PR title and
   description and wait for approval. Then `git push -u origin feature/doc-sync` and call the
   GitHub MCP `create_pull_request` (base `main`, head `feature/doc-sync`) with
   `docs/pr-description.md` as the body. Print the PR URL.

## Gates
Stop and wait at: (1) clarifying questions and my "finalize", (2) design-review decisions,
(3) impl-plan approval, (4) PR title/description approval. If I say "auto", skip gates 2 and 3
only; gates 1 and 4 always apply.

## Never
- Invent facts or test results; paste only real tool output.
- Put secrets in any file, commit or PR. Never push to main.
- If an MCP tool is unavailable, say so and ask me to paste the input instead.
