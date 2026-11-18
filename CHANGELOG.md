# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `doc_sync` CLI (`python -m doc_sync [REPO_PATH]`, console script `doc_sync = doc_sync.cli:main`) that scans a repository and writes `docs/PROJECT_DOC.md` with seven fixed sections.
- Readers for `pyproject.toml`, `README.md`, `requirements.txt`, entry points, language detection by file extension, and the last git commit.
- Atomic, deterministic output writer; missing data is written as `Not Found`.
- Test suite: 257 tests (253 passed, 4 skipped on Windows, 0 failed).
- Agentic SDLC pipeline files (`.claude/` agents, commands, hooks, skill) and pipeline documents in `docs/`.

### Changed
- `.gitignore` reduced; `README.md` updated.

### Fixed
- Headings injected through the Name, HTML, blockquote or list content can no longer change the document structure (CR-1, CR-2).
- Credentials and URL query tokens are stripped from dependency lines; backslash continuations are joined (CR-5, CR-6).
- Windows junctions are pruned in the repo walk; CLI errors are hardened; output file mode is preserved; an empty path is rejected (CR-3, CR-4, CR-8, CR-10).
- `find_git` and last-commit validation hardened (CR-7, CR-9).

### Security
- `pip-audit`: No known vulnerabilities found. Runtime uses the standard library only.
