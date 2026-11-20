---
paths:
  - "src/doc_sync/**/*.py"
  - "tests/**/*.py"
  - "docs/code-review.md"
  - "docs/implementation-report.md"
---

# Code Review Rules

## 1. Independent Review

- Review the actual implementation.
- Compare code with approved requirements and architecture.
- Review implementation evidence.
- Do not assume that reported behavior is correct without inspection.

## 2. Seven Required Review Areas

Evaluate:

1. Correctness.
2. Security.
3. Error Handling.
4. Test Coverage.
5. Code Clarity.
6. DRY Principle.
7. Dependency Safety.

Do not silently skip a review area.

If evidence is unavailable, report the limitation.

## 3. Evidence Standards

- Findings must be supported by actual code or test evidence.
- Include accurate file paths.
- Include line numbers when available.
- Do not invent defects, vulnerabilities, or test results.
- Distinguish confirmed defects from recommendations.
- Use `Not Found` for unavailable information.

## 4. Security Standards

- Never expose secrets in the review report.
- Identify hardcoded credentials without reproducing their values.
- Check input validation and sensitive logging.
- Do not claim security validation is complete without evidence.

## 5. Test Standards

- Inspect positive, negative, and edge-case tests.
- Check missing-file and `Not Found` scenarios.
- Do not claim tests passed unless they were executed successfully.
- Report unexecuted checks as Not Run.

## 6. Review Restrictions

- Do not modify source code or tests.
- Do not change requirements or architecture.
- Do not commit or push changes.
- Do not create pull requests.
- Do not start additional subagents.
- Do not update `docs/sdlc-state.md`.

## 7. Report Standards

Update `docs/code-review.md` with:

- Review areas.
- Findings.
- Severity.
- Evidence.
- Impact.
- Recommended actions.
- Review verdict.
- Limitations.

The main orchestrator handles human approval and pipeline-state updates.
