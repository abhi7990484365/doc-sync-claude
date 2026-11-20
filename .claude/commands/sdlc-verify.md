---
description: Verify implementation, unit tests, integration tests, and final documentation.
argument-hint: "[optional verification focus]"
disable-model-invocation: true
---

# SDLC Step 7: Verification

You are the main SDLC orchestrator.

Coordinate the verification agent and maintain pipeline governance.

## Step 1: Validate Pipeline State

Read:

docs/sdlc-state.md

Confirm:

- Step 6 – Code Review is completed.
- Human approval for code review is recorded.
- The review verdict is APPROVED or APPROVED_WITH_CONDITIONS with accepted conditions.
- Step 7 – Verification is not already completed.

If approval is missing or the review verdict is CHANGES_REQUIRED or BLOCKED, stop.

## Step 2: Validate Input Documents

Read:

- docs/requirements.md
- docs/architecture-design.md
- docs/impl-plan.md
- docs/implementation-report.md
- docs/code-review.md

Confirm that required documents are available and approved.

Inspect the implementation and existing tests.

## Step 3: Delegate Verification

Use the Agent tool to delegate to:

sdlc-verification-agent

Provide:

- Approved requirements.
- Approved architecture.
- Implementation plan.
- Implementation report.
- Code review report.
- Source and test directories.
- Optional verification focus supplied as command arguments.

Instruct the agent to verify both the code and final output documentation.

## Step 4: Validate Verification Output

Inspect:

docs/verification-report.md

Confirm that:

- Unit tests were executed where applicable.
- Integration tests were executed where applicable.
- Actual commands and results are recorded.
- Failed and skipped tests are identified.
- Documentation quality checks are recorded.
- Missing checks are clearly marked Not Run.
- No unsupported success claims are made.

## Step 5: Handle Failures

If verification fails:

- Present the failed checks to the user.
- Identify the related implementation tasks.
- Request approval to send defects back to the developer agent.
- Do not mark Step 7 completed.

After fixes, rerun the affected verification checks and update the report.

If verification is blocked, document the blockers and stop.

## Step 6: Human Approval

Present the verification summary and report to the user.

Wait for explicit human approval.

## Step 7: Update Pipeline State

Only after approval, update docs/sdlc-state.md:

- Mark Step 7 – Verification as completed.
- Record the verification verdict.
- Record human approval.
- Record docs/verification-report.md as the output.
- Set Step 8 – PR as the next step.

Do not create a PR automatically unless explicitly authorized.

## Restrictions

- Do not perform implementation directly.
- Do not silently fix code defects.
- Do not skip human approval.
- Do not commit or push.
- Do not create a pull request.
- Do not update pipeline state before approval.
