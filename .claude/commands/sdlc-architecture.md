---
description: Agentic SDLC - Architecture Design.
argument-hint: "[optional architecture instructions]"
disable-model-invocation: true
---

# SDLC Step 2 – Architecture Design

Additional instructions: $ARGUMENTS

## Objective

Generate a technical architecture document using
the approved requirements.

## Step 1: Validate Pipeline State

Read:

docs/sdlc-state.md

Verify:

- Requirements step is completed.
- Requirements approval status is approved.
- No unresolved blocking issues exist.
- Current pipeline stage permits architecture design.

If the state file is missing or requirements are not
approved, stop and report the blocker.

## Step 2: Validate Input

Read:

docs/requirements.md

Verify:

- File exists and is readable.
- Requirements are approved.
- Functional requirements are present.
- Non-functional requirements are present.
- Acceptance criteria are documented.
- Open questions and assumptions are identified.

Do not proceed if the requirements are not approved.

## Step 3: Delegate Architecture Work

Use the Agent tool to invoke the architect subagent.

Provide:

- Approved docs/requirements.md
- Relevant project-wide instructions
- Relevant architecture rules and skill

Instruct the agent to generate:

docs/architecture.md

The agent must follow its own definition and
architecture skill.

## Step 4: Validate Output

After the agent completes, inspect docs/architecture.md.

Verify:

- All relevant requirements are addressed.
- Architecture components are identified.
- Component responsibilities are clear.
- Technology choices are justified.
- Data flow is documented.
- Error handling is addressed.
- Security considerations are documented.
- Assumptions and open questions are separated.
- No application code was implemented.

If validation fails, return specific findings to the
architect agent for correction.

## Step 5: Human Approval

Present the architecture document to the user.

Do not mark the architecture step as approved until
the user explicitly approves it.

## Step 6: Update Pipeline State

The main orchestrator must update:

docs/sdlc-state.md

Record:

- Step: Architecture
- Output: docs/architecture.md
- Execution status
- Approval status
- Validation evidence
- Remaining blockers

Only record verified information.

## Step 7: Completion

Report:

- Architecture document location.
- Validation results.
- Important decisions.
- Open questions.
- Approval status.

Do not start design review or implementation planning.
