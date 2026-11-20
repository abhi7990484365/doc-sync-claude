---
name: architecture
description: Reusable architecture design methodology for the doc_sync Python CLI. Use when analyzing approved requirements and creating architecture documentation.
---

# Architecture Design Skill

## 1. Purpose

Define a technical architecture from approved business
and functional requirements.

The architecture must be modular, maintainable,
testable and suitable for Python 3.11.

## 2. Input Requirements

Read:

docs/requirements.md

Do not design from unapproved requirements.

## 3. Architecture Design Process

### Step 1: Requirement Analysis

- Identify functional requirements.
- Identify non-functional requirements.
- Identify external integrations.
- Identify constraints and dependencies.
- Identify security requirements.
- Identify unresolved questions.

### Step 2: Component Identification

Identify the minimum components required.

For each component define:

- Component name.
- Responsibility.
- Input.
- Output.
- Dependencies.
- Error conditions.

Avoid creating components without a clear responsibility.

### Step 3: Technology Selection

Evaluate technologies based on:

- Python 3.11 compatibility.
- Simplicity.
- Maintainability.
- Security.
- Testing support.
- Dependency footprint.

For every recommendation document:

- Technology.
- Purpose.
- Reason for selection.
- Alternatives considered.
- Trade-offs.

Do not introduce dependencies without justification.

### Step 4: Data Flow Design

Document the complete application flow.

Consider:

1. CLI input.
2. Configuration loading.
3. Repository discovery.
4. File and metadata scanning.
5. Data extraction.
6. Data transformation.
7. Documentation generation.
8. Output validation.
9. Error reporting.

Only include stages supported by requirements
or explicitly identified as recommendations.

### Step 5: Error Handling

Consider:

- Empty repository.
- Missing files.
- Invalid configuration.
- Unsupported file types.
- Permission errors.
- API failures, if applicable.
- File read/write failures.
- Invalid input.

Ensure recoverable failures are handled gracefully.

### Step 6: Security Design

Document:

- Environment-based credentials.
- Secret redaction.
- Safe logging.
- File access boundaries.
- Input validation.
- Sensitive data handling.

Never include actual credentials in architecture documents.

### Step 7: Testing Architecture

Define:

- Unit testing.
- Integration testing.
- CLI testing.
- Error and edge-case testing.
- Test data strategy.
- Mocking strategy where required.

Use pytest as the testing framework.

### Step 8: Technical Decisions

Document significant architectural decisions.

For each decision include:

- Decision ID.
- Context.
- Selected approach.
- Reasoning.
- Alternatives.
- Trade-offs.
- Status.

Do not invent decision IDs or claim approval
without evidence.

## 4. Architecture Principles

- Prefer modular design.
- Follow single responsibility.
- Minimize coupling.
- Avoid unnecessary abstractions.
- Reuse shared utilities.
- Keep components independently testable.
- Separate business logic from CLI handling.
- Keep configuration separate from implementation.
- Handle errors explicitly.
- Design for maintainability.

## 5. Documentation Standards

Generate:

docs/architecture.md

Use the following sections:

1. Architecture Overview
2. Requirements Mapping
3. Architecture Diagram
4. Technology Stack
5. Component Design
6. Data Flow
7. Error Handling
8. Security Architecture
9. Testing Architecture
10. Technical Decisions
11. Assumptions
12. Open Questions

Use Mermaid diagrams when they clarify architecture.

Use exactly "Not Found" for unavailable information.

Separate confirmed facts from recommendations.

## 6. Quality Validation

Before completing:

- Check requirements traceability.
- Check component responsibilities.
- Check component dependencies.
- Check data flow completeness.
- Check security considerations.
- Check testability.
- Check consistency across diagrams and descriptions.
- Check that no unsupported assumptions are presented
  as confirmed facts.

## 7. Scope Restrictions

This skill covers architecture design only.

Do not:

- Implement Python code.
- Create pytest test files.
- Modify requirements.md.
- Create implementation plans.
- Perform formal design reviews.
- Create pull requests.