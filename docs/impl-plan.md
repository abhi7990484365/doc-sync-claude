# Implementation Plan: Automated Documentation Sync

Inputs: `docs/architecture.md` (revised), `docs/design-review.md` (DR-1..DR-15 Accepted), `docs/requirements.md` (FR-1..FR-28, NFR-1..NFR-6).
Each task is one developer invocation and includes its tests. Every function has type hints; no duplicated logic (shared helpers from `fs`, `markdown`, `collect.first_present`, `render`, `git_info.run_git`).
OI-7 / DR-11 (ignore `.venv`, `node_modules`, `.gitignore`) is open and NOT implemented. Only `.git` and the output file are skipped.
Paths below are relative to the repo root. Standard library only at runtime; `pytest` is the only dev tool.

## Tasks

| ID | Task (goal) | Files | Requirements | Blocked by | Acceptance check | Status |
|---|---|---|---|---|---|---|
| T-1 | Scaffolding. Create the package layout, `pyproject.toml` with `[project]` (Python >=3.11) and `[project.scripts] doc_sync = "doc_sync.cli:main"`, pytest config so `src/` is importable, and `requirements.txt` listing dev tools (pytest). Build backend: Not Found in architecture; developer picks the minimal one needed for `pip install -e .` and notes it. | create `pyproject.toml`, `requirements.txt`, `src/doc_sync/__init__.py`, `tests/__init__.py` (if needed), `tests/test_packaging.py` | FR-1, NFR-1 | none | `pytest tests/test_packaging.py` passes: `pyproject.toml` declares `doc_sync = "doc_sync.cli:main"` under `[project.scripts]`; `import doc_sync` works | Done |
| T-2 | `fs.py`: `read_text` (`utf-8-sig`, returns `None` on `OSError`/`UnicodeDecodeError`) and `iter_repo_files` (`os.walk` with `onerror` ignore, prunes `.git`, skips `docs/PROJECT_DOC.md`, no symlinked dirs, sorted). | create `src/doc_sync/fs.py`, `tests/test_fs.py` | FR-6, FR-11, FR-28, NFR-6 | T-1 | `pytest tests/test_fs.py`: BOM dropped, missing/undecodable file gives `None`, `.git` and output file excluded, empty dir gives `[]`, result sorted | Done |
| T-3 | `markdown.py`: `Heading`, `atx_heading`, `setext_level`, `fence_flags`, `find_headings` per the Markdown rules (``` and ~~~ fences, closing `#` run, setext, heading directly followed by text). | create `src/doc_sync/markdown.py`, `tests/test_markdown.py` | FR-28, FR-14, FR-15, FR-16 | T-1 | `pytest tests/test_markdown.py`: ATX and setext detection, closing `#` run, fence open/close for both markers and lengths, unclosed fence marker returned, headings in fences ignored | Done |
| T-4 | `pyproject.py`: `load_pyproject` (missing or invalid TOML gives `{}`), `project_table`, `project_field`, `project_scripts` (`<name> = <target>`, declared order, non-string entries skipped). | create `src/doc_sync/pyproject.py`, `tests/test_pyproject.py` | FR-5, FR-11, FR-13, FR-15, FR-16 | T-2 | `pytest tests/test_pyproject.py`: name/description/scripts read; invalid TOML and missing file; non-table `project`/`scripts`; non-string keys/values; blank name gives `None` | Done |
| T-5 | `readme.py`: `load_readme`, `first_heading`, `first_paragraph`, `section_body` (first Usage/How to Run heading in document order, same-or-higher-level end, empty body gives `None`). | create `src/doc_sync/readme.py`, `tests/test_readme.py` | FR-5, FR-14, FR-15, FR-16, FR-28 | T-2, T-3 | `pytest tests/test_readme.py`: ATX and setext first heading, first paragraph, Usage and How to Run, absent section, first match wins, empty first match gives `None`, headings in fences ignored, BOM file | Done |
| T-6 | `languages.py`: `EXTENSION_LANGUAGES` (table from architecture) and `detect_languages` (`suffix.lower()`, unique, sorted, unknown ignored). | create `src/doc_sync/languages.py`, `tests/test_languages.py` | FR-6, FR-20, NFR-6 | T-2 | `pytest tests/test_languages.py`: table mapping, case-insensitive, unknown ignored, dedupe and sort, `.git` contents excluded (via `iter_repo_files`) | Done |
| T-7 | `dependencies.py`: `strip_url_credentials`, `clean_requirement`, `parse_requirements`, `read_dependencies`. | create `src/doc_sync/dependencies.py`, `tests/test_dependencies.py` | FR-7, FR-9, FR-26, NFR-2 | T-2 | `pytest tests/test_dependencies.py`: comments and blanks skipped, missing file gives `[]`, `-r`/`--index-url` skipped, `user:pass@` and `token@` removed, inline ` #` stripped, `pkg @ https://...` kept without credentials, `${VAR}` stays literal, dummy token never in output | Done |
| T-8 | `entry_points.py`: `entry_point_files` (`__main__.py`/`main.py`, repo-relative POSIX, sorted) and `collect_entry_points` (scripts first, then files). | create `src/doc_sync/entry_points.py`, `tests/test_entry_points.py` | FR-13 | T-2, T-4 | `pytest tests/test_entry_points.py`: scripts plus files in order, nested files, `.git` excluded, none gives `[]` | Done |
| T-9 | `git_info.py` part 1: `find_git` (own PATH walk, skips cwd/root/empty/`.`, `git.exe` on Windows), `git_env` (drops `GIT_*`), `run_git` (the only subprocess site; argv list, `shell=False`, timeout 10, stdin DEVNULL, `None` on failure/timeout/`OSError`). | create `src/doc_sync/git_info.py`, `tests/test_git_info.py` | FR-11, NFR-2, NFR-3 | T-1 | `pytest tests/test_git_info.py -k "find_git or env or run_git"`: planted `git`/`git.exe` in root and cwd not chosen, `GIT_DIR` absent from child env, `shell=False` and argv list (monkeypatched `subprocess.run`), timeout, non-zero code, and missing git give `None` | Done |
| T-10 | `git_info.py` part 2: `is_top_level` (normcase of resolved paths) and `last_commit` (flags `--no-show-signature --no-color --format=%h %ad %s --date=short`; output must match `[0-9a-f]{4,40} \d{4}-\d{2}-\d{2} \S.*` on one line). | modify `src/doc_sync/git_info.py`, `tests/test_git_info.py` | FR-8, FR-19, FR-27, FR-11 | T-9 | `pytest tests/test_git_info.py`: real temp repo gives `<sha> YYYY-MM-DD <subject>` (skip if git unavailable), non-repo and no commits give `None`, plain folder inside a repo gives `None`, invalid or multi-line output gives `None` | Done |
| T-11 | `collect.py`: frozen `ProjectInfo`, `first_present`, `collect(root)` (loads pyproject and README once, walks files once, assembles all fields, no exceptions escape). | create `src/doc_sync/collect.py`, `tests/test_collect.py`, `tests/test_precedence.py` | FR-5, FR-11, FR-12, FR-15, FR-16, FR-13, FR-14, NFR-5 | T-4, T-5, T-6, T-7, T-8, T-10 | `pytest tests/test_collect.py tests/test_precedence.py`: pyproject wins, fallback per field independently, empty dir gives all `None`/`[]`, no invented values | Todo |
| T-12 | `render.py`: `NOT_FOUND`, `SECTION_ORDER`, `single_line`, `safe_body`, `render_text`, `render_list`, `render_document` (title, 7 sections, single trailing newline). | create `src/doc_sync/render.py`, `tests/test_render.py` | FR-3, FR-4, FR-9, FR-10, FR-28, NFR-5 | T-3, T-11 | `pytest tests/test_render.py`: title line, exact order and count of 7 level-2 headings, `- item` lists, exact `Not Found`, embedded `#`/`##` demoted to `###`, setext underline escaped, unclosed fence closed, multi-line name collapsed | Todo |
| T-13 | `writer.py`: `atomic_write` (`mkstemp` in `docs`, UTF-8 `errors="replace"`, `\n`, `os.replace`, temp removed in `finally`, re-raise `OSError`) and `write_doc` (`mkdir(parents=True, exist_ok=True)`). | create `src/doc_sync/writer.py`, `tests/test_writer.py` | FR-2, FR-18, FR-21, FR-25, NFR-6 | T-1 | `pytest tests/test_writer.py`: creates `docs/`, overwrites, `docs` is a file and `PROJECT_DOC.md` is a directory raise `OSError`, no temp file left, existing file unchanged when `os.replace` fails | Todo |
| T-14 | `cli.py` and `__main__.py`: `parse_args`, `resolve_repo`, `path_error`, `main` (exit 0 / 2 / 1; prints `Wrote <path>`; one-line stderr, no traceback); `sys.exit(cli.main())` in `__main__`. | create `src/doc_sync/cli.py`, `src/doc_sync/__main__.py`, `tests/test_cli.py`, `tests/test_main_module.py` | FR-1, FR-2, FR-17, FR-22, FR-23, FR-24, FR-25, NFR-2, NFR-4 | T-11, T-12, T-13 | `pytest tests/test_cli.py tests/test_main_module.py`: default cwd, explicit path, exit 0 with `Not Found`, missing path exit 2 with `REPO_PATH not found: <path>` and no file, file path exit 2 with `REPO_PATH is not a directory`, write failure exit 1 with one stderr line and no `Traceback`, success line has no env values, `python -m doc_sync <missing>` exits 2 | Todo |
| T-15 | `test_annotations.py`: import every `doc_sync` module and use `inspect` to check all parameters (except `self`/`cls`) and return types are annotated. | create `tests/test_annotations.py` | NFR-1 | T-14 | `pytest tests/test_annotations.py` passes for all modules | Todo |
| T-16 | End-to-end tests on fixture repos in `tmp_path`: full repo, empty repo, determinism, secret env var, embedded `##` README. Fix any gaps found in earlier modules. | create `tests/test_end_to_end.py` | FR-2, FR-4, FR-11, FR-12, FR-28, NFR-2, NFR-4, NFR-6 | T-14 | `pytest tests/test_end_to_end.py`: full repo output correct, empty repo all `Not Found` and exit 0, two runs identical, dummy secret env var absent from output and console, README with `##` keeps exactly 7 level-2 sections | Todo |
| T-17 | NFR-5 review and full run: check for duplicated logic and single-purpose functions (one file reader, one heading/fence rule set, one `Not Found` site, one subprocess site); fix findings; run the whole suite. | modify `src/doc_sync/*.py` only if findings; no new files | NFR-5, NFR-4 | T-15, T-16 | `pytest` (all) passes; `grep` shows `subprocess.run` only in `git_info.run_git` and `"Not Found"` only in `render.NOT_FOUND`; findings listed in the commit message or PR | Todo |

## Requirement-to-Task Coverage

| Req | Tasks |
|---|---|
| FR-1 | T-1, T-14 |
| FR-2 | T-13, T-14, T-16 |
| FR-3 | T-12 |
| FR-4 | T-12, T-16 |
| FR-5 | T-4, T-5, T-11 |
| FR-6 | T-2, T-6 |
| FR-7 | T-7 |
| FR-8 | T-10 |
| FR-9 | T-7, T-12 |
| FR-10 | T-12 |
| FR-11 | T-2, T-4, T-9, T-10, T-11, T-16 |
| FR-12 | T-11, T-16 |
| FR-13 | T-4, T-8, T-11 |
| FR-14 | T-3, T-5, T-11 |
| FR-15 | T-3, T-4, T-5, T-11 |
| FR-16 | T-3, T-4, T-5, T-11 |
| FR-17 | T-14 |
| FR-18 | T-13 |
| FR-19 | T-10 |
| FR-20 | T-6 |
| FR-21 | T-13 |
| FR-22 | T-14 |
| FR-23 | T-14 |
| FR-24 | T-14 |
| FR-25 | T-13, T-14 |
| FR-26 | T-7 |
| FR-27 | T-10 |
| FR-28 | T-2, T-3, T-5, T-12, T-16 |
| NFR-1 | T-1, T-15 |
| NFR-2 | T-7, T-9, T-14, T-16 |
| NFR-3 | T-9 |
| NFR-4 | T-14, T-16, T-17 |
| NFR-5 | T-11, T-12, T-17 |
| NFR-6 | T-2, T-6, T-13, T-16 |

## Blocked / Not Specified
- No task is Blocked.
- Not Found: build backend for `pyproject.toml` is not named in the architecture (T-1). The developer chooses the minimal one and records it.
- Not implemented by design: OI-7 / DR-11 (ignore lists for `.venv`, `node_modules`, `.gitignore`). No task exists until a requirement is answered.
