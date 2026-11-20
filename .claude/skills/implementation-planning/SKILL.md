---
name: implementation-planning
description: Breaks approved software architecture into small, prioritized, dependency-ordered and testable implementation tasks.
---

# Implementation Planning Skill

## 1. Purpose

Convert approved requirements, architecture and design
review findings into an actionable implementation plan.

## 2. Input Documents

- docs/requirements.md
- docs/architecture-design.md
- docs/design-review.md

## 3. Planning Methodology

### Step 1: Understand the Architecture

Identify:

- Application components.
- Component responsibilities.
- Internal dependencies.
- External integrations.
- Data flows.
- Security requirements.
- Testing architecture.

### Step 2: Identify Workstreams

Group development tasks into logical workstreams.

Possible workstreams include:

- Project setup and configuration.
- CLI implementation.
- Repository scanning.
- Data extraction.
- Data transformation.
- Documentation generation.
- Error handling.
- Security.
- Testing.
- Integration and packaging.

Only include workstreams supported by approved architecture.

### Step 3: Break Down Tasks

Break each workstream into small, independently
understandable tasks.

Each task should:

- Have one clear objective.
- Be independently implementable where possible.
- Have defined inputs and outputs.
- Identify affected components.
- Include acceptance criteria.
- Include testing requirements.

Avoid tasks that combine unrelated responsibilities.

### Step 4: Define Dependencies

For each task identify:

- Prerequisite tasks.
- Dependent tasks.
- Tasks that can run independently.
- Tasks blocked by unresolved decisions.

Never create circular dependencies.

### Step 5: Prioritize Tasks

Use these priorities:

### P0 – Critical

Required foundational work that blocks subsequent tasks.

### P1 – High

Essential functionality required for the application.

### P2 – Medium

Supporting functionality and quality improvements.

### P3 – Low

Optional improvements that are not required for
the initial working release.

Justify priorities based on project requirements
and dependencies.

### Step 6: Define Implementation Order

Order tasks using:

1. Dependency requirements.
2. Foundational components.
3. Core application functionality.
4. Integration.
5. Error handling and security.
6. Testing and validation.
7. Packaging and final verification.

Do not force an order between independent tasks.

### Step 7: Identify Blockers

For each blocked task document:

- Task ID.
- Blocking dependency or decision.
- Reason for blockage.
- Required resolution.

Use exactly "Not Found" for unavailable information.

### Step 8: Define Testing Activities

Identify relevant tests for each task.

Consider:

- Unit tests.
- Integration tests.
- CLI tests.
- Positive scenarios.
- Negative scenarios.
- Edge cases.
- Regression tests.

Use pytest.

### Step 9: Define Completion Criteria

Every task must have measurable acceptance criteria.

Examples:

- Module can be imported successfully.
- Expected output is generated.
- Invalid input is handled correctly.
- Required pytest tests pass.

Do not claim execution results during planning.

## 4. Task ID Convention

Use sequential identifiers:

- TASK-001
- TASK-002
- TASK-003

Never reuse task IDs within the plan.

## 5. Output Structure

Generate:

docs/impl-plan.md

Include:

1. Planning Overview
2. Architecture Reference
3. Implementation Workstreams
4. Prioritized Task Breakdown
5. Dependency Mapping
6. Implementation Sequence
7. Parallelizable Tasks
8. Blocked Tasks
9. Testing Activities
10. Risks and Mitigations
11. Definition of Done
12. Approval Status

## 6. Quality Validation

Before completing:

- Verify task traceability.
- Verify all dependencies exist.
- Check for circular dependencies.
- Check implementation order.
- Verify task priorities.
- Verify testing coverage.
- Verify blocked tasks.
- Verify acceptance criteria.
- Check that no implementation has been performed.

## 7. Scope Restrictions

This skill covers implementation planning only.

Do not:

- Write Python code.
- Create application modules.
- Execute implementation tasks.
- Create Git commits.
- Modify approved architecture.
- Start code review or verification.
