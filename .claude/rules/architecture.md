---
paths:
  - "docs/architecture.md"
---

# Architecture Documentation Rules

## Accuracy

- Use approved requirements as the source of truth.
- Never invent requirements or business facts.
- Separate confirmed decisions from recommendations.
- Use exactly "Not Found" for unavailable information.

## Design Quality

- Prefer simple, modular architecture.
- Every component must have a clear responsibility.
- Avoid unnecessary dependencies and abstractions.
- Document component interactions and dependencies.
- Keep architecture diagrams consistent with descriptions.

## Technology Decisions

- Python 3.11 is mandatory.
- Justify every recommended technology.
- Explain important trade-offs.
- Do not claim a technology is approved without evidence.

## Documentation

- Maintain requirements traceability.
- Include error-handling and security considerations.
- Document assumptions and open questions separately.
- Use Mermaid diagrams where useful.
- Keep terminology consistent throughout the document.

## Scope

- Architecture documentation only.
- Do not include implementation code.
- Do not mark architecture as approved without human approval.
