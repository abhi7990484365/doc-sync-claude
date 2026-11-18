# Requirements: Automated Documentation Sync

Source: `docs/user-story.md` (with acceptance criteria). Format: `.claude/skills/doc-sync-format/SKILL.md`.
Status: regenerated; acceptance criteria treated as confirmed answers.

## Overview
A Python 3.11 CLI, invoked as `doc_sync [REPO_PATH]`, scans a repository and writes
`docs/PROJECT_DOC.md` so documentation stays in sync with the code. Data that cannot be
found is written as exactly `Not Found`. Failures (empty repo, missing file, git error)
never crash the tool. No secrets are ever printed or written.

## Functional Requirements
- FR-1: The CLI is invoked as `doc_sync [REPO_PATH]`; `REPO_PATH` is optional. (story)
- FR-2: The tool scans the repository and writes `docs/PROJECT_DOC.md`. (story)
- FR-3: The file starts with one `# <Name>` title line, or `# Not Found` if the name is unknown. (doc-sync-format)
- FR-4: The file contains exactly these level-2 sections, in this order, none omitted: `## Name`, `## Description`, `## Languages`, `## Dependencies`, `## Entry Points`, `## How to Run`, `## Last Commit`. (story AC1; doc-sync-format)
- FR-5: Name and Description are read from `pyproject.toml` or from the first paragraph of `README.md`. (story AC2)
- FR-6: Languages are detected from file extensions; files under `.git` are ignored. (story AC3)
- FR-7: Dependencies are read from `requirements.txt`. (story AC4)
- FR-8: Last Commit is read from git and rendered as `<short-sha> <date> <subject>`. (story AC5; doc-sync-format)
- FR-9: Languages, Dependencies and Entry Points are rendered as `- item` lines; an empty list is `Not Found`. (doc-sync-format)
- FR-10: Any missing, unreadable or empty data makes the section body exactly `Not Found` (case and spacing exact, no punctuation, no extra words). (story AC6; doc-sync-format)
- FR-11: An empty repo, a missing source file, or a git failure does not crash the tool; only the affected section(s) become `Not Found`. (story AC7)
- FR-12: The tool never guesses or invents content; only data found in the repo is written. (doc-sync-format; CLAUDE.md)

## Non-Functional Requirements
- NFR-1: Runs on Python 3.11; every function signature has type hints. (story; CLAUDE.md)
- NFR-2: No credentials, secrets or environment variable values appear in the output file, console output or logs. (story AC8; doc-sync-format)
- NFR-3: Any credentials, if ever needed, come only from environment variables. (CLAUDE.md)
- NFR-4: Every behaviour is covered by a pytest test in `tests/`, including each failure mode in FR-11 (no crash, `Not Found` output). (CLAUDE.md; story AC7)
- NFR-5: Small single-purpose functions; no duplicated logic (shared helpers, e.g. one `Not Found` renderer). (CLAUDE.md)

## Clarification Log
| Question | Answer |
|---|---|
| Q1 Where do Name and Description come from? | `pyproject.toml` or first paragraph of `README.md` (story AC2) |
| Q2 How are Languages detected? | From file extensions, ignoring `.git` (story AC3) |
| Q3 How are Dependencies detected? | From `requirements.txt` (story AC4) |
| Q4 Last Commit source and format? | git, `<short-sha> <date> <subject>` (story AC5) |
| Q5 Behaviour on missing data / failures? | Exactly `Not Found`; empty repo, missing file, git failure must not crash (story AC6, AC7) |
| Q6 CLI interface? | `doc_sync [REPO_PATH]` (story) |
| Q7 Which external API(s)? | Only git is named in the story; no other API: Not Found |

## Open Items
- OI-1: Source of Entry Points and How to Run: Not Found.
- OI-2: Precedence when both `pyproject.toml` and `README.md` provide Name/Description: Not Found.
- OI-3: Default `REPO_PATH` when omitted, and whether `docs/PROJECT_DOC.md` is written inside `REPO_PATH`: Not Found.
- OI-4: Date format in Last Commit and the extension-to-language mapping: Not Found.
- OI-5: Exit codes and overwrite behaviour for an existing `PROJECT_DOC.md`; behaviour when `REPO_PATH` does not exist: Not Found.
- OI-6: Confluence/Jira source for the story: none supplied.
