---
name: pull-request
description: Guidelines for preparing evidence-based GitHub pull requests, changelog entries, test evidence, reviewer checklists, and safe PR creation.
---

# Pull Request Skill

## 1. Objective

Prepare and create a GitHub pull request for the completed and verified implementation.

The PR must provide reviewers with enough information to understand the changes, inspect the implementation, and validate the test evidence.

## 2. Required Documents

Read:

1. docs/requirements.md
2. docs/architecture-design.md
3. docs/design-review.md
4. docs/impl-plan.md
5. docs/implementation-report.md
6. docs/code-review.md
7. docs/verification-report.md

Inspect the actual Git changes before preparing the PR.

## 3. Pre-PR Validation

Confirm:

- Implementation is completed.
- Code review is approved.
- Verification is approved.
- Required human approvals are recorded.
- No blocking defects remain.
- Current branch is feature/doc-sync.
- Target branch is main.
- Changed files are understood.
- No credentials or secrets are included.

If any condition is not satisfied, stop and report the issue.

## 4. PR Title

Use a concise title that describes the actual change.

Preferred format:

```text
feat: implement automated documentation sync
```

Do not claim functionality that has not been implemented.

## 5. PR Description

Every PR must contain the following sections.

### Summary

Provide 2–3 sentences describing:

- What was implemented.
- Why the change was necessary.
- The main outcome.

### Changes Made

List relevant added and modified files.

Example:

| File | Change | Purpose |
|---|---|---|
| src/doc_sync/scanner.py | Added | Repository scanning |
| tests/test_scanner.py | Added | Scanner tests |
| docs/PROJECT_DOC.md | Generated | Project documentation |

Use actual Git evidence. Do not invent files.

### Test Evidence

Include:

- Test commands actually executed.
- Actual test results.
- Relevant unit test results.
- Relevant integration test results.
- CI links only when available.

Never claim tests passed without execution evidence.

### Known Limitations

Include:

- Information marked Not Found.
- Incomplete implementation items.
- Out-of-scope functionality.
- Accepted verification limitations.

If no limitations were identified, state that based on available evidence.

### Reviewer Checklist

Provide actionable reviewer checklist items.

Examples:

- [ ] Requirements are addressed.
- [ ] Architecture is followed.
- [ ] Error handling is appropriate.
- [ ] No secrets are exposed.
- [ ] Tests cover positive and negative scenarios.
- [ ] Documentation is accurate.
- [ ] Changelog is included.

## 6. Changelog Entry

Prepare a concise changelog entry describing the user-visible or project-relevant changes.

Use the repository's existing changelog format if one exists.

If no changelog exists, prepare an appropriate CHANGELOG.md entry.

Do not overwrite existing changelog history.

## 7. Git Safety

Source branch:

feature/doc-sync

Target branch:

main

Rules:

- Never create a PR from main.
- Never force-push.
- Never rewrite existing commit history.
- Never discard uncommitted user changes.
- Do not stage unrelated files.
- Do not include secrets.
- Do not push or create a PR without explicit authorization.

Use Conventional Commit conventions:

- feat:
- fix:
- test:
- refactor:
- docs:
- chore:

## 8. GitHub PR Creation

Use GitHub CLI if available.

Before creating the PR:

- Check GitHub CLI availability.
- Confirm authentication without displaying credentials.
- Confirm the current branch.
- Confirm the target branch.
- Confirm the changes are committed and pushed as authorized.
- Confirm the final PR description.

If GitHub access is unavailable, report the issue.

Never fabricate a PR number, URL, or creation result.

## 9. PR Report

Update:

docs/pr-report.md

Record:

- PR title.
- PR description.
- Source branch.
- Target branch.
- Changelog entry.
- Reviewer checklist.
- Test evidence.
- Known limitations.
- Actual PR number and URL, if created.
- Creation status.

## 10. Scope Restrictions

- Do not modify requirements.
- Do not redesign architecture.
- Do not silently modify implementation code.
- Do not invent test results.
- Do not expose credentials.
- Do not force-push.
- Do not push directly to main.
- Do not create a PR without human approval.

## 11. Completion Criteria

The PR stage is complete only when:

- Verification is approved.
- PR content is prepared.
- Changelog entry is prepared.
- Reviewer checklist is included.
- Human approval is received.
- GitHub confirms successful PR creation.
- Actual PR details are recorded.
- docs/pr-report.md is updated.
