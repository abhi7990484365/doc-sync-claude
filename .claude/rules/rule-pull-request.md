---
paths:
  - "docs/pr-report.md"
  - "CHANGELOG.md"
---

# Pull Request Rules

## 1. Approval Requirements

- Implementation must be completed.
- Code review must be approved.
- Verification must be approved.
- Human approval is required before PR creation.

## 2. Required PR Sections

Every PR description must include:

1. Summary.
2. Changes Made.
3. Test Evidence.
4. Known Limitations.
5. Reviewer Checklist.

The Summary must contain 2–3 sentences.

## 3. Evidence Standards

- Use actual Git changes.
- Include actual test results.
- Use real CI links only.
- Document known limitations.
- Never invent PR numbers, URLs, or commit hashes.
- Use `Not Found` for missing information.

## 4. Changelog Rules

- Follow the existing changelog format.
- Do not overwrite existing history.
- Describe actual implemented changes.
- Do not include unsupported functionality.

## 5. Git Rules

- Source branch must be `feature/doc-sync`.
- Target branch must be `main`.
- Never force-push.
- Never push directly to main.
- Never discard user changes.
- Do not stage unrelated files.
- Do not commit secrets.

## 6. Security Rules

- Never expose tokens or passwords.
- Never include credentials in PR descriptions.
- Never include sensitive environment values in changelog entries or reports.

## 7. PR Creation Restrictions

- Do not create a PR without explicit human approval.
- Do not create a PR if verification failed or is blocked.
- Do not claim PR creation without GitHub confirmation.
- Do not fabricate PR URLs or numbers.

## 8. Final Reporting

Update docs/pr-report.md with the actual PR details and creation status.

The main orchestrator is responsible for updating docs/sdlc-state.md.
