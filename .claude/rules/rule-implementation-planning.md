---
paths:
  - "docs/impl-plan.md"
---

# SDLC Implementation Planning Rules

## Accuracy

- Use approved requirements and architecture.
- Consider approved design-review findings.
- Never invent requirements, components or dependencies.
- Separate confirmed decisions from recommendations.
- Use exactly "Not Found" for unavailable information.

## Task Quality

- Every task must have a unique ID.
- Tasks must be small and actionable.
- Every task must have a clear objective.
- Include expected outputs and affected components.
- Include measurable acceptance criteria.
- Include relevant testing activities.

## Dependency Management

- Document all known task dependencies.
- Never create circular dependencies.
- Identify parallelizable tasks.
- Identify blocked tasks and their reasons.
- Do not mark blocked tasks as ready.

## Prioritization

- Use P0, P1, P2 and P3 priorities.
- Justify critical and high-priority tasks.
- Respect architectural dependencies.
- Avoid unnecessary work outside the approved scope.

## Quality

- Include positive and negative testing activities.
- Consider edge cases.
- Include security and error-handling work.
- Do not claim tests have passed during planning.
- Do not invent execution evidence.

## Pipeline Governance

- Do not start implementation.
- Do not modify approved requirements or architecture.
- Require human approval before development begins.
- Update pipeline state only through the main orchestrator.
