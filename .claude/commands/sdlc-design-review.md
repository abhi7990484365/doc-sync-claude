---
description: Agentic SDLC - Architecture Design Review.
argument-hint: "[optional review instructions]"
disable-model-invocation: true
---

# SDLC Step 3 – Design Review

Additional instructions: $ARGUMENTS

## Objective

Independently review the approved system architecture
before implementation planning.

## Step 1: Validate Pipeline State

Read:

docs/sdlc-state.md

Verify:

- Architecture step is completed.
- Architecture approval status is approved.
- Requirements approval status is approved.
- No blocking issues prevent design review.

If validation fails, stop and report the blocker.

## Step 2: Validate Input Documents

Read:

- docs/requirements.md
- docs/architecture-design.md

Verify both documents exist and are approved.

Do not proceed with unapproved inputs.

## Step 3: Delegate Design Review

Use the Agent tool to invoke:

sdlc-design-reviewer

Provide:

- Approved requirements.
- Approved architecture.
- Relevant project rules and skill.

Request an independent review.

Generate:

docs/design-review.md

## Step 4: Validate Review Output

Inspect docs/design-review.md.

Verify:

- All review categories are covered.
- Findings have supporting evidence.
- Severity levels are assigned.
- Recommendations are actionable.
- Risks and unresolved questions are documented.
- Overall verdict is clearly stated.

If validation fails, send specific findings to the reviewer
for correction.

## Step 5: Architecture Changes

If findings require architecture changes:

- Do not silently modify the approved architecture.
- Present the findings to the orchestrator.
- Require human decision on proposed changes.
- If changes are approved, update architecture-design.md
  through the appropriate architecture workflow.
- Re-run the design review against the revised architecture.

## Step 6: Human Approval

Present the review report to the user.

Require explicit approval before marking this stage complete.

## Step 7: Update Pipeline State

The main orchestrator updates:

docs/sdlc-state.md

Record:

- Design review execution status.
- Review output location.
- Review verdict.
- Findings summary.
- Architecture revision status.
- Human approval status.

Only record verified information.

## Step 8: Completion

Return:

- Review report location.
- Findings summary.
- Overall verdict.
- Required architecture changes.
- Approval status.

Do not start implementation planning.