---
description: Independently review the implementation before verification.
argument-hint: "[optional review focus]"
disable-model-invocation: true
---

# SDLC Step 6: Code Review

You are the main SDLC orchestrator.

Coordinate the independent code review and maintain pipeline governance.

## Step 1: Validate Pipeline State

Read:

`docs/sdlc-state.md`

Confirm:

- Step 5 – Implementation is completed.
- Human approval for implementation is recorded.
- Step 6 – Code Review is not already completed.

If implementation approval is missing, stop and request approval.

## Step 2: Validate Review Inputs

Read:

- `docs/requirements.md`
- `docs/architecture-design.md`
- `docs/design-review.md`
- `docs/impl-plan.md`
- `docs/implementation-report.md`

Confirm that required documents exist and have appropriate approval.

Inspect the current source code and tests.

If required inputs are missing, report the issue instead of guessing.

## Step 3: Delegate Code Review

Use the Agent tool to delegate to:

`sdlc-code-reviewer`

Provide:

- Approved requirements.
- Approved architecture.
- Design review findings.
- Implementation plan.
- Implementation report.
- Source code and test locations.
- Optional review focus supplied as command arguments.

Ask the reviewer to evaluate all seven review areas.

The reviewer must not modify implementation files.

## Step 4: Validate Review Output

Inspect:

`docs/code-review.md`

Confirm that:

- All seven review areas were evaluated.
- Findings include evidence.
- Severity levels are assigned consistently.
- File paths and line numbers are accurate where provided.
- Recommendations are actionable.
- The verdict is supported by the findings.

Do not accept invented test results or unsupported vulnerability claims.

## Step 5: Handle Review Findings

If the verdict is `CHANGES_REQUIRED`:

- Present findings to the user.
- Request approval to send required fixes back to the developer agent.
- Do not mark Step 6 completed.
- Preserve the review report and findings.

If the verdict is `BLOCKED`:

- Report the missing inputs or blockers.
- Do not proceed to verification.

If the verdict is `APPROVED_WITH_CONDITIONS`:

- Present the remaining conditions.
- Request human approval to proceed.

If the verdict is `APPROVED`:

- Present the review summary.
- Request human approval before updating pipeline state.

## Step 6: Update Pipeline State

Only after the required human approval:

Update `docs/sdlc-state.md`:

- Mark Step 6 – Code Review as completed.
- Record the review verdict.
- Record the approval status.
- Record `docs/code-review.md` as the output.
- Set Step 7 – Verify as the next step.

Do not start Step 7 automatically unless explicitly authorized.

## Restrictions

- Do not perform code review directly in the orchestrator.
- Do not modify implementation files.
- Do not skip human approval.
- Do not create a pull request.
- Do not commit or push changes.
- Do not update pipeline state before approval.
