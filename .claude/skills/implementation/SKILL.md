---
name: implementation
description: Guidelines for implementing approved Python development tasks, writing pytest tests, and reporting implementation evidence.
---

# Implementation Skill

## Objective

Implement approved tasks from `docs/impl-plan.md` according to the requirements and architecture.

## Required Reading Order

1. `docs/requirements.md`
2. `docs/architecture-design.md`
3. `docs/design-review.md`
4. `docs/impl-plan.md`

Do not begin implementation until the required approvals are confirmed.

## 1. Understand the Task

For each task:

- Identify its task ID.
- Understand its objective.
- Identify related requirements.
- Review its dependencies.
- Identify expected source files.
- Identify expected tests.
- Identify its acceptance criteria.

Do not implement tasks with unresolved dependencies.

## 2. Inspect Existing Code

Before creating or modifying files:

- Inspect the existing project structure.
- Search for reusable functions and classes.
- Check existing coding conventions.
- Avoid duplicating existing functionality.
- Preserve unrelated user changes.

Prefer modifying existing files over creating unnecessary alternatives.

## 3. Implementation Standards

- Python version: 3.11.
- Use type hints for every function signature.
- Use clear variable and function names.
- Keep functions small and single-purpose.
- Use appropriate exception handling.
- Avoid unnecessary dependencies.
- Keep business logic separate from CLI and file operations where appropriate.
- Follow the approved architecture.

## 4. Project Structure

Follow the existing project structure. The expected locations are:

```text
src/
└── employee_app/
    ├── __init__.py
    └── ...

tests/
├── __init__.py
└── ...