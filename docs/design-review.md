# Design Review

Input: `docs/architecture.md` (reviewed against `docs/requirements.md`, CLAUDE.md, doc-sync-format skill).
Verdict: all 29 requirement ids are covered; safe to implement once High/Medium findings are resolved.
Decision values: Accept / Reject / Defer. Current state: all Pending (GATE 2).

| Id | Sev | Area | Finding | Recommended change | Decision |
|---|---|---|---|---|---|
| DR-1 | High | Security | `parse_requirements` keeps lines as written; pip option lines/URLs (`--index-url https://user:token@host`, `pkg @ https://token@...`) and inline comments could leak credentials into PROJECT_DOC.md (NFR-2, FR-7). | Skip lines starting with `-`; strip `user:pass@`/`token@` from URLs; strip inline ` #` comments; add tests. | Pending |
| DR-2 | Med | Security | `run_git` uses bare `git`; on Windows cwd is searched first (FR-17), so a planted `git.exe` could run. Inherited `GIT_DIR`/`GIT_WORK_TREE` can redirect git. | Resolve absolute git path excluding cwd/repo root (or set `NoDefaultCurrentDirectoryInExePath`); drop `GIT_*` vars from child env; add test. | Pending |
| DR-3 | Med | Correctness | User git config (`log.showSignature`, `color.ui=always`) can alter `git log` output (FR-19). | Add `--no-show-signature --no-color` (or `-c` overrides); validate against `^\S+ \d{4}-\d{2}-\d{2} `, else `None`. | Pending |
| DR-4 | Med | Correctness | `git -C root` searches upward; a plain folder inside another repo reports the outer repo's commit (FR-11, FR-12). | Compare `git rev-parse --show-toplevel` to `root`, else `None`; or document as accepted; add test. | Pending |
| DR-5 | Med | Correctness | `section_body` can include `##` headings (e.g. README `# Usage`, multi-line description), adding extra level-2 sections (FR-4). | In `render_text`, demote embedded headings to `###`+ or reject such bodies; add test. | Pending |
| DR-6 | Med | Correctness | README parser ignores fenced code blocks; `# comment` inside a fence is read as a heading (FR-14/15/16). | Track fences (``` / ~~~) and ignore headings inside; add tests. | Pending |
| DR-7 | Med | Error handling | Type checks only for `[project].name/description`; non-table `project`/`project.scripts` or non-string targets could raise (FR-11). | Specify type checks for `project`, `scripts`, keys and values; failures give `[]`/`None`; add tests. | Pending |
| DR-8 | Med | Correctness | `__main__.py` calls `cli.main()` without `sys.exit(...)`, so `python -m doc_sync` exits 0 on failure (FR-22/23). | Use `sys.exit(cli.main())`; add subprocess test expecting exit 2 on missing path. | Pending |
| DR-9 | Med | Open case: REPO_PATH is a file | Exit 2 reasonable, but data flow says `resolve_repo` returns `None` only if the path doesn't exist, conflicting with the `is_dir()` rule; message "not found" misleading; no test; no FR. | Accept exit 2; `resolve_repo` returns `None` when `not is_dir()`; separate message "REPO_PATH is not a directory"; add `test_cli.py` case; add a new FR. | Pending |
| DR-10 | Med | Open case: output not writable | Exit 1 reasonable, but no test for exit 1/stderr; unclear `test_writer.py` wording; uncovered: `docs` is a file, `PROJECT_DOC.md` is a directory, truncated partial writes; no FR. | Accept exit 1 with one-line stderr, no traceback; write temp file then `os.replace`; add tests for both blocked paths; add a new FR. | Pending |
| DR-11 | Low | Correctness | Only `.git` excluded; `.venv`/`node_modules` get scanned, polluting Languages and Entry Points (FR-6, FR-13). | Raise as a requirements question (ignore list / `.gitignore`); don't change design without a requirement. | Pending |
| DR-12 | Low | Correctness | UTF-8 BOM breaks `first_heading`; setext headings unsupported; heading directly followed by text unspecified (FR-15/16). | Read as `utf-8-sig`; specify setext and heading+text handling; add tests. | Pending |
| DR-13 | Low | Correctness | `section_body` unspecified when both `Usage` and `How to Run` exist or first match is empty (FR-14). | First matching heading in document order; empty body gives `None`; add test. | Pending |
| DR-14 | Low | Test coverage | NFR-1 check is "mypy --strict or annotation check" (not a fixed pytest); no test for the console-script declaration (FR-1). | Commit to a pytest checking full annotations; add test that pyproject declares `doc_sync = "doc_sync.cli:main"`. | Pending |
| DR-15 | Low | Traceability | Design-only behaviours (path is a file, write failure) have no requirement ids. | After new FRs from DR-9/DR-10, add traceability rows; until then list as untraced. | Pending |

## Held up without changes
Traceability of FR-1..23 / NFR-1..6; subprocess safety (arg list, no shell, closed stdin, timeout, stderr discarded); single place producing `Not Found`; repeatable output; shared helpers (NFR-5); standard-library only.
