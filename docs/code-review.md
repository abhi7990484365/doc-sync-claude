# Code Review

Scope: `src/doc_sync/*.py`, `tests/*.py` vs requirements, architecture, design review, CLAUDE.md.
Evidence: `python -m pytest -q` = 214 passed, 1 skipped (T-2 symlink test, skipped on Windows).
`pip-audit -r requirements.txt` (real output): "No known vulnerabilities found" (exit 0). Only a harmless `WARNING:venv` path note.
Reviewer ran no commands; CR-3 and CR-4 (Windows behaviour) come from reading the code, not from running it.
OI-7 (skip `.venv`/`node_modules`) is intentionally not implemented and not raised.

## Verdicts

| Area | Verdict | Basis |
|---|---|---|
| Correctness | Concern | CR-1, CR-2, CR-3, CR-6, CR-7, CR-10 |
| Security | Concern | CR-5, CR-1/CR-2 (structure injection), CR-8, CR-9. `shell=False`, argv list, `GIT_*` removal, discarded git stderr are correct |
| Error Handling | Concern | CR-3, CR-4. Atomic write cleanup and exit 1/2 paths are correct |
| Test Coverage | Concern | CR-13 |
| Code Clarity | Pass | minor CR-11 |
| DRY | Pass | minor CR-12 |
| Dependency Safety | Pass | pip-audit clean; runtime is standard library only |

## Findings

| Id | Sev | Area | Finding | Evidence | Recommended change | Decision |
|---|---|---|---|---|---|---|
| CR-1 | Med | Correctness/Security (FR-4, FR-28) | Name body only goes through `single_line`, not `safe_body`. `name = "## Evil"` yields an 8th level-2 heading; `# X` a second level-1. | render.py:94-96, 80-89; markdown.py:93; test_render.py:98-101 | Send Name through the shared safe helper (or escape leading `#`); test `name="## Evil"`. | Accept |
| CR-2 | Med | Correctness (FR-28) | `safe_body` only demotes line-start ATX headings. Raw HTML `<h1>/<h2>`, blockquote `> ## x`, list `- # x` pass through; READMEs starting with `<h1 align="center">` make a level-1 heading in Description. `render_list` items like `## x` too. | render.py:28-33, 73-77; markdown.py:9; readme.py:39-50 | Escape leading `#` after `>`/`-`/`*`/`+`/digit markers; escape or skip `<h1>`..`<h6>` lines; optionally skip HTML-only lines in `first_paragraph`. | Accept |
| CR-3 | Med | Correctness/Error handling (Windows) | NTFS junctions are followed in the walk (`islink` is False for junctions), so files outside the repo count, and a junction to a parent can recurse. Only symlink test is skipped on Windows. | fs.py:28-31; test_fs.py:74-83 | Also prune reparse points (`st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT`); add a Windows junction test. | Accept |
| CR-4 | Med | Error handling (FR-22/25, Windows) | `print(f"Wrote {target}")` is outside the `try`; non-encodable path under redirected stdout raises `UnicodeEncodeError` after the file is written. `collect` is inside the write `try`, so collect `OSError`s say "Could not write document". `Path.cwd()` can raise uncaught if the cwd was deleted. | cli.py:26, 50, 55 | Write success line with `backslashreplace`; move collect/render out of the write `try`; catch `OSError` from `Path.cwd()` and exit 2. | Accept |
| CR-5 | Med | Security (NFR-2) | Tokens in URL query strings are kept: `pkg @ https://host/pkg.whl?token=abc123`. Userinfo, `git+https://user:pass@`, `file:///`, `;` markers, `-` lines are handled. | dependencies.py:11; test_dependencies.py:54-66 | Drop or mask the query string of URLs (or at least token/key/secret/password/auth params); add test. | Accept |
| CR-6 | Low | Correctness (FR-7/12) | Backslash continuations are not joined; hash-pinned files render `- pkg==1.0 \`. | dependencies.py:30-33 | Join `\` lines before cleaning; strip `--hash` options. | Accept |
| CR-7 | Low | Correctness (FR-27) | `COMMIT_PATTERN` `.` accepts `\x0b \x0c \x1c-\x1e \x85    `; `splitlines()` then makes Last Commit multi-line. Format issue, not injection. | git_info.py:12; render.py:58 | Reject unless `len(out.splitlines()) == 1`, or exclude those chars in the pattern. | Accept |
| CR-8 | Low | Security (POSIX) | `mkstemp` makes the file 0600 and `os.replace` keeps it, so `PROJECT_DOC.md` becomes owner-only and overwrites any existing mode. N/A on Windows. | writer.py:15-19 | `os.chmod(tmp, existing_mode or 0o666 & ~umask)` before replace. | Accept |
| CR-9 | Low | Security (DR-2) | `find_git` accepts relative PATH entries under the cwd (e.g. `bin`, `.\tools`); a planted `git.exe` there could run. | git_info.py:55-60 | Skip non-absolute entries and/or anything inside cwd; add test. | Accept |
| CR-10 | Low | Correctness (FR-23) | `doc_sync ""` silently uses the cwd (`if args.repo_path`). | cli.py:26 | `is not None`, so an empty path fails as not found; or document it. | Accept |
| CR-11 | Low | Clarity | Code differs from architecture: stderr text, temp prefix `.doc-sync-` vs `.PROJECT_DOC.`, `resolve_repo` does not resolve, `_readme_field(parser: Any)` loses type safety. | cli.py:32,53; writer.py:15; collect.py:49 | Update architecture.md to match; type `parser` as `Callable[[str], str \| None]`. | Accept |
| CR-12 | Low | DRY (NFR-5) | Output path defined twice (`fs.OUTPUT_RELATIVE`, `writer.DOCS_DIR/OUTPUT_NAME`); `collect._is_dir` repeats `resolve_repo` check. | fs.py:9; writer.py:9-10; collect.py:41-46 | Keep one constant in `fs.py`, import in `writer.py`. | Accept |
| CR-13 | Low | Test coverage (NFR-4) | No tests for: leading-`#` Name, HTML/blockquote/list headings, junctions, non-encodable stdout, query-string tokens, `\` continuations, `fs` `onerror`, relative PATH entries. | tests/ | Add the tests listed with each accepted finding. | Accept |
