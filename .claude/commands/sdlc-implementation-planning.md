---
description: Agentic SDLC - Implementation Planning.
argument-hint: "[optional planning instructions]"
disable-model-invocation: true
---

# SDLC Step 4 – Implementation Planning

Additional instructions: $ARGUMENTS

## Objective

Generate a prioritized and dependency-ordered
implementation plan using approved SDLC documents.

## Step 1: Validate Pipeline State

Read:

docs/sdlc-state.md

Verify:

- Requirements are completed and approved.
- Architecture is completed and approved.
- Design review is completed and approved.
- No blocking design-review findings remain.
- The pipeline permits implementation planning.

If validation fails, stop and report the blocker.

## Step 2: Validate Input Documents

Read:

- docs/requirements.md
- docs/architecture-design.md
- docs/design-review.md

Verify:

- All documents exist and are readable.
- Requirements and architecture are approved.
- Design review has an approved verdict.
- Required architecture changes have been incorporated.
- No unresolved blocking decisions remain.

Do not proceed with unapproved inputs.

## Step 3: Delegate Planning

Use the Agent tool to invoke:

sdlc-implementation-planner

Provide the approved input documents and relevant
project instructions.

Request a dependency-ordered implementation plan.

Generate:

docs/impl-plan.md

## Step 4: Validate Implementation Plan

Inspect docs/impl-plan.md.

Verify:

- Every task has a unique task ID.
- Tasks map to approved requirements or architecture.
- Dependencies reference existing tasks.
- No circular dependencies exist.
- Tasks are ordered correctly.
- Priorities are justified.
- Testing activities are identified.
- Blocked tasks are documented.
- Acceptance criteria are measurable.
- Parallelizable tasks are identified where applicable.

If validation fails, return specific findings to the
planner agent for correction.

## Step 5: Human Approval

Present the implementation plan to the user.

Do not mark the plan as approved until explicit
human approval is received.

## Step 6: Update Pipeline State

The main orchestrator updates:

docs/sdlc-state.md

Record:

- Step: Implementation Planning
- Output: docs/impl-plan.md
- Execution status
- Task count
- Blocked task count
- Approval status
- Validation evidence

Only record verified information.

## Step 7: Completion

Return:

- Implementation plan location
- Total tasks
- Priority distribution
- Dependency summary
- Blocked tasks
- Approval status

Do not start implementation.
