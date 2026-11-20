---
description: Implement approved tasks from the SDLC implementation plan.
argument-hint: "[optional task IDs]"
disable-model-invocation: true
---

# SDLC Step 5: Implementation

You are the main SDLC orchestrator.

Your responsibility is to coordinate implementation and maintain workflow governance.

## Step 1: Validate Pipeline State

Read:

- `docs/sdlc-state.md`

Confirm that:

- Step 4 – Implementation Planning is completed.
- The implementation plan has human approval.
- Step 5 – Implementation is not already completed.

If the required approval is missing, stop and request approval from the user.

## Step 2: Validate Input Documents

Read and validate:

- `docs/requirements.md`
- `docs/architecture-design.md`
- `docs/design-review.md`
- `docs/impl-plan.md`

Confirm that the documents are available and approved.

Do not proceed if required documents are missing or contain unresolved blocking issues.

## Step 3: Delegate Implementation

Use the Agent tool to delegate the work to:

`sdlc-developer`

Provide the agent with:

- The approved requirements.
- The approved architecture.
- The design review findings.
- The approved implementation plan.
- Optional task IDs supplied as command arguments.

Instruct the agent to implement only the approved tasks.

The developer agent must not start additional subagents.

## Step 4: Validate Implementation Output

After the developer agent finishes, inspect:

- Source code changes.
- Test code changes.
- `docs/implementation-report.md`.

Confirm that:

- Planned tasks are accurately reported.
- New behavior has corresponding tests.
- Test results are based on actual execution.
- Incomplete work and blockers are documented.
- No unrelated files or requirements were changed.

Do not mark the step complete if implementation is incomplete or blocked.

## Step 5: Human Review

Present the implementation summary and report to the user.

Wait for explicit human approval before marking Step 5 as completed.

## Step 6: Update Pipeline State

Only after approval, update `docs/sdlc-state.md`:

- Mark Step 5 – Implementation as completed.
- Record the approval status.
- Record the implementation report path.
- Identify Step 6 – Code Review as the next step.

Do not start Step 6 automatically unless the user or orchestrator workflow explicitly authorizes it.

## Important Restrictions

- Do not implement code directly in the orchestrator.
- Do not skip human approval.
- Do not invent test results.
- Do not modify the approved architecture.
- Do not commit or push changes.
- Do not update pipeline state before human approval.