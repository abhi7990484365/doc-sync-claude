# User Story: Automated Documentation Sync

Source: pasted (use case from capstone project statement; no Confluence page supplied).

As a developer, I want a small Python 3.11 CLI that scans a repository and generates
`docs/PROJECT_DOC.md`, so that project documentation stays in sync with the code.
Anything the tool cannot find must be written as exactly "Not Found".

Required sections of PROJECT_DOC.md (see .claude/skills/doc-sync-format/SKILL.md):
Name, Description, Languages, Dependencies, Entry Points, How to Run, Last Commit.

Constraints: handle API failures, missing files and empty repos; never expose secrets;
credentials only via environment variables.
