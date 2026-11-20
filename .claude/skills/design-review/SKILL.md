---
name: design-review
description: Structured technical architecture review methodology covering requirements traceability, component design, security, maintainability and technical risks.
---

# Design Review Skill

## 1. Purpose

Independently evaluate the technical architecture
against approved requirements.

## 2. Input Documents

- docs/requirements.md
- docs/architecture-design.md

## 3. Review Methodology

### Step 1: Requirements Traceability

- Check whether requirements are addressed.
- Identify missing requirements.
- Identify unsupported architecture decisions.
- Check requirement-to-component mapping.

### Step 2: Architecture Completeness

- Check whether all necessary components are defined.
- Verify component responsibilities.
- Identify missing interactions.
- Identify unnecessary components.

### Step 3: Component Design

Evaluate:

- Single responsibility.
- Coupling.
- Cohesion.
- Reusability.
- Maintainability.
- Testability.

### Step 4: Technology Review

- Validate Python 3.11 compatibility.
- Evaluate proposed dependencies.
- Review technology justifications.
- Identify unnecessary packages.
- Identify alternatives and trade-offs.

### Step 5: Data Flow Review

- Verify data flow completeness.
- Check input and output handling.
- Identify missing validation.
- Review file handling and data transformations.

### Step 6: Error Handling Review

Evaluate:

- Missing files.
- Empty repositories.
- Invalid configuration.
- Permission errors.
- API failures, if applicable.
- File read/write failures.
- Unexpected exceptions.

### Step 7: Security Review

Evaluate:

- Credential handling.
- Environment variables.
- Secret exposure.
- Sensitive information in logs.
- File access restrictions.
- Input validation.

### Step 8: Testing Architecture Review

Evaluate:

- Unit testing.
- Integration testing.
- CLI testing.
- Negative scenarios.
- Edge cases.
- Testability of individual components.

### Step 9: Maintainability Review

Evaluate:

- Code organization.
- Separation of concerns.
- Dependency management.
- Complexity.
- Duplication risks.

## 4. Finding Severity

Use these severity levels:

### Critical

A fundamental architecture or security issue
that prevents safe implementation.

### High

A significant design gap likely to cause
incorrect behavior, security risk or major rework.

### Medium

A design weakness that should be addressed
before or during implementation.

### Low

A minor improvement or maintainability suggestion.

### Informational

An observation that does not require a change.

## 5. Finding Format

Each finding must include:

- Finding ID.
- Review category.
- Severity.
- Description.
- Evidence.
- Impact.
- Recommendation.
- Status.

Do not invent evidence or IDs.

## 6. Review Verdict

Use one of these verdicts:

- APPROVED
- APPROVED_WITH_CONDITIONS
- CHANGES_REQUIRED
- BLOCKED

Verdicts must be supported by actual findings.

## 7. Output Structure

Generate:

docs/design-review.md

Include:

1. Review Overview
2. Scope
3. Review Summary
4. Requirements Traceability
5. Review Findings
6. Risk Assessment
7. Recommendations
8. Architecture Changes Required
9. Unresolved Questions
10. Overall Verdict
11. Approval Status

## 8. Quality Standards

- Every finding must have supporting evidence.
- Avoid duplicate findings.
- Recommendations must be actionable.
- Separate observations from confirmed defects.
- Do not invent missing information.
- Use exactly "Not Found" for unavailable information.

## 9. Scope Restrictions

- Review architecture only.
- Do not implement code.
- Do not modify approved requirements.
- Do not independently approve architecture.
- Do not create implementation plans.
