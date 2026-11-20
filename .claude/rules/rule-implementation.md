---
paths:
  - "src/doc_sync/**/*.py"
  - "tests/**/*.py"
  - "docs/implementation-report.md"
---

# Implementation Rules

## 1. Python Standards

- Use Python 3.11.
- Add type hints to every function signature.
- Use clear and descriptive names.
- Keep functions small and focused on one responsibility.
- Avoid duplicated code.
- Follow the approved architecture.
- Avoid unnecessary dependencies.
- Follow existing project conventions.

## 2. Implementation Scope

- Implement only tasks listed in the approved `docs/impl-plan.md`.
- Follow the approved requirements and architecture.
- Do not independently change requirements or architecture.
- Do not introduce unrelated refactoring.
- Do not implement tasks with unresolved dependencies.
- Report unclear requirements to the orchestrator.

## 3. Testing Standards

- Use pytest.
- Every new behavior must have a corresponding test.
- Cover positive, negative, and relevant edge cases.
- Test missing files and empty repositories where applicable.
- Keep tests independent and maintainable.
- Do not remove or weaken existing tests just to make them pass.
- Run relevant tests after implementation.
- Never report a test as passed unless it was actually executed successfully.

## 4. Error Handling

Handle expected failures gracefully, including:

- Missing files.
- Empty repositories.
- Invalid input.
- Permission errors.
- API failures.
- Unexpected empty values.

Use the exact text `Not Found` for missing data.

Do not silently ignore errors or invent missing information.

## 5. Security Rules

- Read credentials only from environment variables.
- Never hardcode credentials.
- Never print or log secrets.
- Never write tokens or passwords into source files, test files, or reports.
- Do not expose sensitive information in test output.
- Do not commit credentials or other sensitive data.

## 6. Git Rules

- Work only on the `feature/doc-sync` branch.
- Check the current branch before making changes.
- Preserve existing uncommitted user changes.
- Never commit directly to `main`.
- Never force-push.
- Do not commit or push unless explicitly authorized by the orchestrator.
- Use Conventional Commit prefixes when a commit is authorized:
  - `feat:`
  - `fix:`
  - `test:`
  - `refactor:`
  - `docs:`
  - `chore:`

## 7. Implementation Report Rules

Update `docs/implementation-report.md` with factual implementation evidence.

Include:

- Implemented task IDs.
- Files created and modified.
- Tests added or updated.
- Actual test commands executed.
- Actual test results.
- Incomplete tasks.
- Blockers and known limitations.

Use `Not Found` for missing information.

Never fabricate implementation status or test results.

## 8. Workflow Restrictions

- Do not modify `docs/sdlc-state.md`.
- Do not perform the independent code review.
- Do not create pull requests.
- Do not start additional subagents.
- Do not communicate directly with the user.
- Return implementation results and blockers to the main orchestrator.
