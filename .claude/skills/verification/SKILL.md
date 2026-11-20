---
name: verification
description: Procedures for comprehensive Python code verification, unit testing, integration testing, regression testing, and generated documentation quality validation.
---

# Verification Skill

## 1. Objective

Verify that the implementation satisfies approved requirements and that the generated PROJECT_DOC.md is accurate and complete.

Verification must be based on actual execution and repository evidence.

## 2. Required Inputs

Read:

1. docs/requirements.md
2. docs/architecture-design.md
3. docs/impl-plan.md
4. docs/implementation-report.md
5. docs/code-review.md

Inspect:

- src/doc_sync/
- tests/
- docs/PROJECT_DOC.md

If the final document does not exist, report it as missing. Do not invent its content.

## 3. Verification Planning

Prepare verification scenarios from:

- Functional requirements.
- Non-functional requirements.
- Acceptance criteria.
- Implementation tasks.
- Code review findings.
- Known limitations.

Map each scenario to its related requirement or task ID when available.

Do not invent requirement IDs.

## 4. Unit Test Verification

Verify individual functions and components.

Cover applicable scenarios:

- Valid input.
- Invalid input.
- Empty input.
- Missing files.
- Empty repositories.
- Missing data.
- Error handling.
- Boundary conditions.

Use pytest.

## 5. Integration Test Verification

Verify interactions between relevant components.

Examples where applicable:

- Repository scanning and file discovery.
- File reading and parsing.
- Documentation generation.
- Output file creation.
- Error propagation between components.

Use the actual architecture to determine integration boundaries.

Do not invent integrations that are not part of the implementation.

## 6. Regression Verification

Run existing tests to identify unintended behavior changes.

Check that new implementation changes have not broken previously working functionality.

Record failed and skipped tests separately.

## 7. Documentation Quality Verification

Inspect docs/PROJECT_DOC.md.

Verify:

### Structure

- Required sections are present.
- Section headings are clear.
- Markdown formatting is valid.
- Tables and lists are properly formatted.

### Accuracy

- Information matches the repository.
- Project details are supported by actual files.
- Commands and configuration details are accurate.
- No unsupported features are documented.

### Missing Information

- Missing values use exactly Not Found.
- Unknown information is not guessed.
- Missing sections are reported.

### Security

- No credentials or tokens are exposed.
- No passwords or sensitive environment values are documented.

## 8. Execution Commands

Run appropriate commands based on the project configuration.

Examples:

```bash
pytest -v
```

```bash
pytest tests/ -v
```

```bash
pytest tests/ -m integration -v
```

Do not assume an integration marker exists. Inspect the project configuration first.

Record every actual command and its result.

If a test cannot run, report Not Run and explain the reason.

## 9. Result Classification

Use these statuses:

- PASS: Check executed successfully.
- FAIL: Check executed and failed.
- BLOCKED: Check could not proceed because of a dependency or blocker.
- NOT RUN: Check was not executed.
- NOT APPLICABLE: Check does not apply to this implementation.

Never report an unexecuted check as PASS.

## 10. Verification Report

Update:

docs/verification-report.md

Include:

- Verification scope.
- Requirement and task traceability.
- Unit test results.
- Integration test results.
- Regression test results.
- Documentation quality results.
- Commands executed.
- Failed checks.
- Blockers.
- Known limitations.
- Overall verdict.

## 11. Overall Verdict

Choose one:

- VERIFIED: All required checks passed.
- VERIFIED_WITH_LIMITATIONS: Required checks passed, with documented non-blocking limitations.
- FAILED: One or more required checks failed.
- BLOCKED: Verification could not be completed.

## 12. Scope Restrictions

- Do not change approved requirements.
- Do not redesign the architecture.
- Do not silently fix implementation defects.
- Do not commit or push.
- Do not create a pull request.
- Do not start additional subagents.
- Do not update docs/sdlc-state.md.

Report defects to the main orchestrator.

## 13. Completion Criteria

Verification is complete when:

- Required unit tests are executed.
- Applicable integration tests are executed.
- Regression checks are completed.
- Final documentation quality is checked.
- Actual results are recorded.
- Failed and unexecuted checks are disclosed.
- docs/verification-report.md is updated.
