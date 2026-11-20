---
paths:
  - "src/employee_app/**/*.py"
  - "tests/**/*.py"
  - "docs/PROJECT_DOC.md"
  - "docs/verification-report.md"
---

# Verification Rules

## 1. Verification Standards

- Verify against approved requirements and architecture.
- Cover applicable unit and integration tests.
- Perform regression checks.
- Validate the final PROJECT_DOC.md.
- Use actual repository evidence.

## 2. Test Execution

- Use pytest.
- Record exact commands.
- Record actual results.
- Separate passed, failed, blocked, skipped, and unexecuted checks.
- Never fabricate test results.
- Never report an unexecuted test as passed.

## 3. Documentation Quality

Check:

- Required sections.
- Markdown formatting.
- Accuracy against repository content.
- Missing information represented as Not Found.
- No invented facts.
- No exposed secrets.

## 4. Evidence and Traceability

- Link checks to actual requirement or task IDs when available.
- Do not invent IDs.
- Record evidence for failures.
- Distinguish confirmed defects from possible risks.
- Record limitations honestly.

## 5. Security

- Never expose credentials in test output.
- Never write tokens or passwords into verification reports.
- Use safe test data.
- Do not commit secrets.

## 6. Scope Restrictions

- Do not silently fix implementation defects.
- Do not change requirements or architecture.
- Do not commit or push.
- Do not create pull requests.
- Do not start additional subagents.
- Do not update docs/sdlc-state.md.

The main orchestrator handles defect routing, human approval, and pipeline-state updates.
