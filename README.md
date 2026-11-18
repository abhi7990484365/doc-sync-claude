# agentic-sdlc
Claude Code pipeline that turns a user story into a GitHub PR (use case: Automated Documentation Sync).
1. Install Python 3.11, then `pip install -r requirements.txt`.
2. Create a GitHub fine-grained PAT for this repo only: Contents and Pull requests read/write.
3. `export GITHUB_PAT=<your token>` (never commit it).
4. Start Claude Code in this folder: `claude`.
5. Run `/mcp` and authenticate `atlassian`; check `github` is connected.
6. Run `/sdlc <Confluence link or pasted user story>`.
7. Answer the analyst's questions, then say `finalize`.
8. Approve design-review decisions, the impl plan and the PR text at each gate (`auto` skips gates 2-3).
9. The PR URL is printed at the end; progress is in `docs/sdlc-state.md`.
10. Run tests anytime with `python -m pytest -q`.

Single steps: `/sdlc-requirements`, `/sdlc-architecture`, `/sdlc-design-review`, `/sdlc-plan`, `/sdlc-implement`, `/sdlc-code-review`, `/sdlc-verify`, `/sdlc-pr`.
