Title: feat: add doc_sync CLI that generates docs/PROJECT_DOC.md

## Summary
Adds `doc_sync`, a Python 3.11 standard-library CLI that scans a repository and writes `docs/PROJECT_DOC.md` with seven fixed sections. Missing data is written as exactly `Not Found`, and the tool does not crash on empty repos, missing files or git failures. The work followed the agentic SDLC pipeline (story, requirements, architecture, reviews, plan, implementation, verification).

## Changes Made
Files from `git diff --stat main...HEAD` (63 files):
- `src/doc_sync/` (`__init__`, `__main__`, `cli`, `collect`, `dependencies`, `entry_points`, `fs`, `git_info`, `languages`, `markdown`, `pyproject`, `readme`, `render`, `writer`): the tool, one single-purpose module each.
- `tests/` (`test_annotations`, `test_cli`, `test_collect`, `test_dependencies`, `test_end_to_end`, `test_entry_points`, `test_fs`, `test_git_info`, `test_languages`, `test_main_module`, `test_markdown`, `test_packaging`, `test_precedence`, `test_pyproject`, `test_readme`, `test_render`, `test_writer`, `.gitkeep`): behaviour tests.
- `pyproject.toml`, `pytest.ini`, `requirements.txt`: packaging, console script, test config, dev dependencies.
- `README.md`, `CLAUDE.md`, `.gitignore`, `.vscode/settings.json`, `.mcp.json`: project docs and configuration.
- `.claude/agents/*` (analyst, architect, developer, planner, pr-writer, reviewer, tester), `.claude/commands/sdlc.md`, `.claude/hooks/*` (`github-mcp-headers.ps1`, `post_edit_pytest.py`, `pre_bash_guard.py`), `.claude/settings.json`, `.claude/skills/doc-sync-format/SKILL.md`: pipeline definition.
- `docs/` (`user-story`, `requirements`, `architecture`, `design-review`, `impl-plan`, `code-review`, `verification-report`, `sdlc-state`, `test-output.txt`, `.gitkeep`): pipeline artefacts.
- `CHANGELOG.md`, `docs/pr-description.md`: added by this step (not yet in the git diff).

All 13 code review findings (CR-1 to CR-13) were accepted and fixed (heading injection, URL query tokens, junctions, CLI errors, file mode, empty path, `find_git`, last-commit validation, shared output path, added tests).

## Test Evidence
From `docs/test-output.txt` (`python -m pytest -v`, Python 3.11.9, pytest 9.2.0, win32):

```
collecting ... collected 257 items
tests/test_writer.py::test_new_file_mode_follows_umask SKIPPED (POSI...) [ 99%]
tests/test_writer.py::test_existing_mode_preserved SKIPPED (POSIX fi...) [ 99%]
======================= 253 passed, 4 skipped in 3.68s ========================
```

- 253 passed, 4 skipped, 0 failed.
- `pip-audit -r requirements.txt`: No known vulnerabilities found.
- Verification: FR 28 PASS, 0 FAIL; NFR 5 PASS, 1 Not Found (NFR-5). See `docs/verification-report.md`.

## Known Limitations
- 4 tests are skipped on Windows (symlink, chmod 000, two POSIX file-mode tests), so those paths are unverified on this platform.
- OI-7 (ignoring `.venv` / `node_modules`) is not implemented; only `.git` is excluded.
- The console script was not exercised via an installed package; only its declaration is checked (`test_packaging.py::test_console_script_declared`).
- NFR-5 is evidenced by code review, not by measurement.
- A README with a multi-line `<h1>` is a known gap.
- No Confluence/Jira source: Not Found.

## Reviewer Checklist
- [ ] Branch is `feature/doc-sync`; nothing committed to `main`
- [ ] `python -m pytest` shows 253 passed, 4 skipped, 0 failed
- [ ] Output has exactly 7 `##` sections; missing data is exactly `Not Found`
- [ ] No tokens or credentials in any file; dependency URLs are sanitised
- [ ] Known Limitations are acceptable
- [ ] Skipped POSIX tests run on Linux/macOS before release
- [ ] `CHANGELOG.md` is accurate

🤖 Generated with [Claude Code](https://claude.com/claude-code)
