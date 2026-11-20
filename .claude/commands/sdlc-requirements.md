---
description: turn a user story into docs/requirements.md
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

---
description: Start the requirements engineering workflow using the Requirements Analyst agent.
argument-hint: "[path-to-user-story]"
disable-model-invocation: true
---

# Requirements Engineering Workflow

Input: $ARGUMENTS

## Instructions

1. Check whether a user story or requirements document was provided.

2. If no input was provided, ask the user to provide a Jira story, Markdown,
   Word document, or plain-text requirement.

3. Read and understand the provided input.

4. Delegate requirements analysis to the
   `requirements-analyst` subagent using the Agent tool.

5. Ensure the analyst follows:
   - Applicable project rules in `.claude/rules/`
   - The preloaded `requirements` skill
   - Global instructions in `CLAUDE.md`

6. The analyst must:
   - Identify business objectives.
   - Identify functional and non-functional requirements.
   - Identify missing information and ambiguities.
   - Ask clarification questions.
   - Wait for user responses.
   - Define Given/When/Then acceptance criteria.
   - Identify positive, negative and edge-case scenarios.

7. Do not generate final requirements documentation
   until clarification questions are resolved or explicitly
   accepted as open questions by the user.

8. Generate the approved draft at:
   `docs/requirements.md`

9. Present the generated document for human review.

10. Do not proceed to architecture design or implementation.

## Expected Output

- Business objectives
- Scope
- Functional requirements
- Non-functional requirements
- Acceptance criteria
- Positive scenarios
- Negative scenarios
- Edge cases
- Assumptions
- Open questions
- Approval status