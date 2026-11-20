---
name: code-review
description: Structured peer-review guidelines for Python implementations, covering correctness, security, error handling, test coverage, clarity, DRY principles, and dependency safety.
---

# Code Review Skill

## 1. Objective

Independently review the implementation before the verification stage.

Evaluate the actual source code, tests, and implementation evidence against the approved requirements and architecture.

Do not modify implementation files.

## 2. Required Inputs

Read:

1. `docs/requirements.md`
2. `docs/architecture-design.md`
3. `docs/design-review.md`
4. `docs/impl-plan.md`
5. `docs/implementation-report.md`

Inspect:

- `src/employee_app/`
- `tests/`
- Dependency configuration and lock files, if available.

## 3. Correctness Review

Check:

- Does each component behave according to the requirements?
- Are acceptance criteria implemented?
- Does the implementation follow the approved architecture?
- Are inputs and outputs handled correctly?
- Is missing data represented as `Not Found`?
- Are there incorrect assumptions or hardcoded values?
- Are there obvious logical errors?

Report confirmed defects with evidence.

## 4. Security Review

Check:

- Are secrets excluded from output?
- Are credentials hardcoded anywhere?
- Are environment variables used for credentials?
- Is user input validated?
- Are sensitive values exposed in exceptions or logs?
- Are files handled safely?
- Are there unsafe operations or insecure configurations?

Never reproduce actual secret values in the review report.

## 5. Error Handling Review

Check whether the implementation handles:

- API failures.
- Missing files.
- Empty repositories.
- Invalid input.
- Permission errors.
- Unexpected empty values.
- File reading and writing failures.

Identify missing exception handling and failures that could terminate the application unexpectedly.

## 6. Test Coverage Review

Inspect tests under `tests/`.

Check:

- Are new behaviors covered?
- Are positive scenarios tested?
- Are negative scenarios tested?
- Are `Not Found` and missing-field cases tested?
- Are boundary conditions covered?
- Are error scenarios covered?
- Are tests independent?
- Are assertions meaningful?

Do not assume tests pass based only on their existence.

If test execution is necessary, use a safe, non-destructive test command and record the actual result.

## 7. Code Clarity Review

Check:

- Are function and variable names self-explanatory?
- Are functions small and focused?
- Is the logic easy to understand?
- Are type hints present on function signatures?
- Is the code organized consistently?
- Are comments useful and necessary?
- Is there unnecessary complexity?

## 8. DRY Principle Review

Check:

- Is the same logic duplicated?
- Are common operations repeated unnecessarily?
- Can repeated logic be handled by an existing shared function?
- Are abstractions appropriate for the project size?

Recommend refactoring only where it improves maintainability.

Avoid suggesting abstractions without a clear benefit.

## 9. Dependency Safety Review

Inspect available dependency files.

Check:

- Are dependencies necessary?
- Are versions declared appropriately?
- Are dependency versions pinned or constrained where required?
- Is there evidence of known vulnerable packages?
- Are obsolete or unnecessary dependencies present?

Use an available dependency audit tool only if it is already installed and can be run safely.

Do not claim a dependency is vulnerable without evidence.

If vulnerability checking was not performed, report it as Not Run.

## 10. Finding Classification

Assign one severity to each finding.

### Critical
Severe security exposure, data loss, or major system failure.

### High
Major functional defect or significant security risk.

### Medium
Important defect, incomplete error handling, or meaningful quality concern.

### Low
Minor maintainability or readability concern.

### Informational
Optional improvement or observation.

Use sequential IDs:

- REVIEW-001
- REVIEW-002
- REVIEW-003

## 11. Review Verdict

Select one verdict:

- APPROVED
- APPROVED_WITH_CONDITIONS
- CHANGES_REQUIRED
- BLOCKED

Apply these rules:

| Verdict | Meaning |
|---|---|
| APPROVED | No unresolved blocking findings |
| APPROVED_WITH_CONDITIONS | Only non-blocking findings remain |
| CHANGES_REQUIRED | Fixes are required before verification |
| BLOCKED | Review cannot be completed due to missing inputs or evidence |

## 12. Review Report

Write the final review to:

`docs/code-review.md`

Include:

- Review summary.
- Seven review areas.
- Findings and evidence.
- Severity classification.
- Recommended actions.
- Overall verdict.
- Open questions and limitations.

Use `Not Found` for unavailable information.

Never invent evidence or results.

## 13. Scope Restrictions

- Do not modify source code.
- Do not modify tests.
- Do not change requirements.
- Do not change architecture.
- Do not create a pull request.
- Do not commit or push.
- Do not start other subagents.
- Do not update `docs/sdlc-state.md`.

Return all findings to the main orchestrator.

## 14. Completion Criteria

The review is complete when:

- All seven review areas are evaluated.
- Findings are documented with evidence.
- Severity is assigned.
- The overall verdict is recorded.
- `docs/code-review.md` is updated.
- Limitations and unverified areas are disclosed.
