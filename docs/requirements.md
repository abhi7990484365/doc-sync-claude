# Requirements: Automated Documentation Sync

Source: `docs/user-story.md` (with acceptance criteria). Format: `.claude/skills/doc-sync-format/SKILL.md`.
Status: final. Acceptance criteria treated as confirmed answers; Open Items OI-1 to OI-5 resolved by user answers (suggested defaults accepted).

## Overview
A Python 3.11 CLI, invoked as `doc_sync [REPO_PATH]`, scans a repository and writes
`<REPO_PATH>/docs/PROJECT_DOC.md` so documentation stays in sync with the code. Data that
cannot be found is written as exactly `Not Found`. Failures (empty repo, missing file, git
error) never crash the tool. No secrets are ever printed or written.

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
- FR-13: Entry Points are collected from `[project.scripts]` in `pyproject.toml` plus any `__main__.py` and `main.py` files in the repo (excluding `.git`). (Q8)
- FR-14: How to Run is taken only from a `README.md` section headed "Usage" or "How to Run"; if no such section exists, the body is `Not Found`. (Q8)
- FR-15: Name precedence: `[project].name` in `pyproject.toml`; if absent, the first heading of `README.md`; otherwise `Not Found`. (Q9; refines FR-5)
- FR-16: Description precedence: `[project].description` in `pyproject.toml`; if absent, the first paragraph of `README.md`; otherwise `Not Found`. Fallback is decided per field independently of Name. (Q9; refines FR-5)
- FR-17: If `REPO_PATH` is omitted, the current working directory is used. (Q10)
- FR-18: Output is written to `<REPO_PATH>/docs/PROJECT_DOC.md`; the `docs/` directory is created if it does not exist. (Q10; refines FR-2)
- FR-19: Last Commit is obtained via `git log -1 --format="%h %ad %s" --date=short`, so the date is `YYYY-MM-DD`. (Q11; refines FR-8)
- FR-20: Languages are mapped from extensions using a fixed built-in extension-to-language table; each language is listed once, sorted alphabetically. Extensions not in the table are ignored. (Q11; refines FR-6)
- FR-21: An existing `PROJECT_DOC.md` is always overwritten. (Q12)
- FR-22: On success the tool exits with code 0, even if some sections are `Not Found`. (Q12)
- FR-23: If `REPO_PATH` does not exist, the tool exits with code 2, prints a short error to stderr, and writes no file. (Q12)

## Non-Functional Requirements
- NFR-1: Runs on Python 3.11; every function signature has type hints. (story; CLAUDE.md)
- NFR-2: No credentials, secrets or environment variable values appear in the output file, console output or logs. (story AC8; doc-sync-format)
- NFR-3: Any credentials, if ever needed, come only from environment variables. (CLAUDE.md)
- NFR-4: Every behaviour is covered by a pytest test in `tests/`, including each failure mode in FR-11 and FR-23 (no crash, `Not Found` output, exit codes). (CLAUDE.md; story AC7)
- NFR-5: Small single-purpose functions; no duplicated logic (shared helpers, e.g. one `Not Found` renderer). (CLAUDE.md)
- NFR-6: Output is deterministic: repeated runs on an unchanged repo produce identical `PROJECT_DOC.md` content (alphabetical languages, overwrite). (Q11, Q12)

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
| Q8 (OI-1) Source of Entry Points and How to Run? | Entry Points: `[project.scripts]` in `pyproject.toml` plus `__main__.py` / `main.py` files. How to Run: only a README "Usage" or "How to Run" section, else `Not Found` (user) |
| Q9 (OI-2) Name/Description precedence? | `pyproject.toml` `[project].name`/`description` wins; README is fallback per field; no pyproject name means README first heading (user) |
| Q10 (OI-3) Default REPO_PATH and output location? | Omitted = current directory; output `<REPO_PATH>/docs/PROJECT_DOC.md`, create `docs/` if needed (user) |
| Q11 (OI-4) Date format and language mapping? | `YYYY-MM-DD` via `git log -1 --format="%h %ad %s" --date=short`; fixed built-in extension-to-language table, sorted alphabetically (user) |
| Q12 (OI-5) Overwrite and exit codes? | Always overwrite; exit 0 on success even with `Not Found` sections; missing REPO_PATH: exit 2, short stderr error, write nothing (user) |

## Open Items
- OI-1: Closed (Q8, FR-13, FR-14).
- OI-2: Closed (Q9, FR-15, FR-16).
- OI-3: Closed (Q10, FR-17, FR-18).
- OI-4: Closed (Q11, FR-19, FR-20). Exact contents of the built-in extension table: Not Found in story; to be defined in design.
- OI-5: Closed (Q12, FR-21 to FR-23).
- OI-6: Closed. No Confluence/Jira source supplied; story was pasted directly.
