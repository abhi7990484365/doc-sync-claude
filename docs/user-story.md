# User Story: Automated Documentation Sync

Source: pasted by the user via `/sdlc` (no Confluence page supplied).

As a developer, I want a Python 3.11 CLI command `doc_sync [REPO_PATH]` that scans a
repository and writes docs/PROJECT_DOC.md, so that project documentation stays in sync
with the code.

## Acceptance criteria
- The file has these sections in order: Name, Description, Languages, Dependencies, Entry Points, How to Run, Last Commit.
- Name and Description come from pyproject.toml or the first paragraph of README.md.
- Languages are detected from file extensions, ignoring .git.
- Dependencies are read from requirements.txt.
- Last Commit comes from git as "<short-sha> <date> <subject>".
- Any missing information is written as exactly "Not Found".
- An empty repo, a missing file or a git failure must not crash the tool; the affected section says "Not Found".
- No credentials or secrets are ever printed or written.

Output format reference: `.claude/skills/doc-sync-format/SKILL.md`.
