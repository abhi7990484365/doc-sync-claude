---
description: Prepare and create the GitHub pull request after successful verification and human approval.
argument-hint: "[optional PR title or additional context]"
disable-model-invocation: true
---

# SDLC Step 8: Pull Request

You are the main SDLC orchestrator.

Coordinate the PR agent and maintain pipeline governance.

## Step 1: Validate Pipeline State

Read:

docs/sdlc-state.md

Confirm:

- Step 5 – Implementation is completed.
- Step 6 – Code Review is completed.
- Step 7 – Verification is completed.
- Human approval is recorded for the required stages.
- Step 8 – Pull Request is not already completed.

If any required stage is incomplete, stop.

## Step 2: Validate Verification Results

Read:

- docs/implementation-report.md
- docs/code-review.md
- docs/verification-report.md

Confirm:

- Code review verdict is APPROVED or accepted APPROVED_WITH_CONDITIONS.
- Verification verdict is VERIFIED or accepted VERIFIED_WITH_LIMITATIONS.
- No unresolved blocking findings remain.
- Test evidence is available.
- Known limitations are documented.

Do not proceed if verification is FAILED or BLOCKED.

## Step 3: Delegate PR Preparation

Use the Agent tool to delegate to:

sdlc-pr-agent

Provide:

- Approved requirements.
- Architecture document.
- Implementation report.
- Code review report.
- Verification report.
- Current Git status.
- Current branch information.
- Optional PR title or context supplied as command arguments.

Ask the agent to prepare:

- PR title.
- PR description.
- Changelog entry.
- Reviewer checklist.
- docs/pr-report.md.

The agent must inspect actual Git changes.

## Step 4: Validate PR Preparation

Inspect docs/pr-report.md.

Confirm that all five required PR sections are present:

1. Summary.
2. Changes Made.
3. Test Evidence.
4. Known Limitations.
5. Reviewer Checklist.

Verify that:

- File changes match Git evidence.
- Test results match verification evidence.
- No secrets are exposed.
- Changelog content is accurate.
- No unsupported claims are included.

## Step 5: Human Approval

Present the following to the user:

- Proposed PR title.
- Complete PR description.
- Changelog entry.
- Source branch and target branch.
- Reviewer checklist.

Ask for explicit approval before creating the PR.

Do not push or create the PR until approval is received.

## Step 6: Create Pull Request

After explicit approval:

1. Confirm the current branch is feature/doc-sync-claude.
2. Confirm the target branch is main.
3. Confirm the working-tree changes are understood.
4. Ensure the authorized changes are committed and pushed without rewriting history.
5. Create the GitHub pull request using the prepared title and description.
6. Capture the actual PR URL and number.
7. Update docs/pr-report.md with the result.

Use GitHub CLI if available and authenticated.

If required GitHub access is unavailable, report the blocker rather than claiming success.

## Step 7: Final Pipeline State

After successful PR creation, update docs/sdlc-state.md:

- Mark Step 8 – Pull Request as completed.
- Record the PR number.
- Record the actual PR URL.
- Record source and target branches.
- Record PR creation status.

Do not mark the PR completed if creation failed.

## Final Summary

Present:

- PR title.
- PR number.
- PR URL.
- Source branch.
- Target branch.
- Changelog location.
- Test evidence.
- Remaining limitations.

## Restrictions

- Do not skip human approval.
- Do not create a PR if verification failed.
- Do not invent PR URLs or numbers.
- Do not expose credentials.
- Never force-push.
- Never push directly to main.
