# Requirements: Automated Documentation Sync

Source: `docs/user-story.md`. Status: draft, no user answers yet.

## Overview
A Python 3.11 CLI (`doc_sync`) scans a repository and generates `docs/PROJECT_DOC.md`
so documentation stays in sync with the code. Any data the tool cannot find is written
as exactly `Not Found`. Output structure is defined by `.claude/skills/doc-sync-format/SKILL.md`.

## Functional Requirements
- FR-1: The CLI scans a repository and writes `docs/PROJECT_DOC.md`. (story: scan + generate)
- FR-2: The file starts with one `# <Name>` title line, or `# Not Found` if the name is unknown. (doc-sync-format)
- FR-3: The file contains exactly these level-2 sections in this order: Name, Description, Languages, Dependencies, Entry Points, How to Run, Last Commit. No section is omitted. (story; doc-sync-format)
- FR-4: If a section's data is missing, unreadable, or the repo is empty, the section body is exactly `Not Found` (case and spacing exact, no punctuation or extra words). (story)
- FR-5: Languages, Dependencies and Entry Points are rendered as `- item` lines; an empty list is `Not Found`. (doc-sync-format)
- FR-6: Last Commit is rendered as `<short-sha> <date> <subject>`, otherwise `Not Found`. (doc-sync-format)
- FR-7: The tool never invents content; only data found in the repo is written. (story; doc-sync-format)
- FR-8: Missing files, an empty repo, and API failures do not crash the tool; the affected sections become `Not Found`. (story constraint)
- FR-9: Re-running the tool on an unchanged repo produces identical output. (story: "stays in sync"; testable derivation)
- FR-10: Credentials, if any are needed, are read only from environment variables. (story constraint)

## Non-Functional Requirements
- NFR-1: Runs on Python 3.11; all function signatures have type hints. (CLAUDE.md)
- NFR-2: No secrets or environment variable values appear in the output file, logs, or console output. (story; CLAUDE.md)
- NFR-3: Every behaviour is covered by a pytest test in `tests/`. (CLAUDE.md)
- NFR-4: The tool is small and single-purpose with no duplicated logic. (story: "small"; CLAUDE.md)
- NFR-5: Failure modes (missing file, empty repo, API error) each have a test showing no crash and `Not Found` output. (story constraint)

## Clarification Log
| Question | Answer |
|---|---|
| Q1 Which API(s) does the tool call? | Pending |
| Q2 Where do Name and Description come from? | Pending |
| Q3 How are Languages and Dependencies detected? | Pending |
| Q4 How are Entry Points and How to Run determined? | Pending |
| Q5 CLI interface (args, output path, exit codes)? | Pending |

## Open Items
- OI-1: Which external API(s), if any, are used (story mentions "API failures") and which environment variables hold credentials: Not Found.
- OI-2: Source of Name and Description (manifest vs README): Not Found.
- OI-3: Supported manifest formats and language detection method: Not Found.
- OI-4: Definition of Entry Points and source of How to Run: Not Found.
- OI-5: CLI arguments, default repo path, overwrite behaviour, exit codes: Not Found.
- OI-6: Behaviour when the target is not a git repo (assumed Last Commit = `Not Found`): unconfirmed.
- OI-7: Any Confluence/Jira source for the story: none supplied.
