# Verification Report

Date: 2026-11-18. Branch `feature/doc-sync`. Python 3.11.9, pytest 9.2.0, Windows 11.
Raw pytest output: `docs/test-output.txt` (unedited, produced with `python -m pytest -v | tee`).

## 1. Test results
- Collected 257; 253 passed, 4 skipped, 0 failed (`253 passed, 4 skipped in 3.68s`).
- Skipped (Windows only, platform limits, not defects):
  - `tests/test_fs.py::test_iter_skips_symlinked_dirs` (symlinks not available)
  - `tests/test_fs.py::test_iter_unreadable_dir_ignored` (chmod 000 not enforced on Windows)
  - `tests/test_writer.py::test_new_file_mode_follows_umask` (POSIX file modes)
  - `tests/test_writer.py::test_existing_mode_preserved` (POSIX file modes)
- Required test categories present: happy path (`test_end_to_end.py::test_full_repo_exact_content`), Not Found (`test_not_found_value_is_exact`, `test_missing_*`), missing field (`test_collect.py::test_readme_only`, `test_precedence.py`), empty repo (`test_empty_repo_all_not_found`, `test_empty_dir_gives_all_missing`), API failure mocked (`test_collect.py::test_last_commit_failure_gives_none`, `test_git_info.py::test_run_git_errors`, `test_run_git_nonzero`). No tests were added.

## 2. Real CLI runs (`PYTHONPATH=src python -m doc_sync <path>`, cwd = repo root, fixtures in a temp dir outside the repo)
| Case | Result |
|---|---|
| Full repo (pyproject, README with Usage, requirements.txt with fake `user:pass@` and `?token=` URLs, git commit, main.py) | exit 0; title `# demo-app`; exactly 7 `##` sections in required order; Languages `- Python`; Dependencies credentials and query token removed, `-r` line skipped, inline comment stripped; Entry Points `- demo = demo.cli:main`, `- main.py`; How to Run from README Usage; Last Commit `25ce0f7 2026-11-18 Initial commit` |
| Second run on full repo | `cmp` byte-identical |
| Fake credential/token grep over generated files, stdout, stderr | no match |
| Empty dir | exit 0; `# Not Found`; all 7 sections exactly `Not Found` |
| Non-git dir with one `.py` | exit 0; Languages `- Python`; Last Commit `Not Found` |
| Missing path | exit 2; stderr `REPO_PATH not found: <path>`; nothing written |
| File path | exit 2; stderr `REPO_PATH is not a directory` |
| `docs` is a file | exit 1; one-line stderr `Could not write document: ...`, no traceback |
| Repo copy of this project (temp dir; real `docs/PROJECT_DOC.md` untouched, `git status` shows only `docs/test-output.txt`) | exit 0; 7 sections; Name `doc_sync`; Languages PowerShell, Python; Dependencies pytest, pip-audit; Entry Points `doc_sync = doc_sync.cli:main`, `src/doc_sync/__main__.py`; How to Run `Not Found` (README has no Usage section); Last Commit `a8538c7 2026-11-18 docs: sync architecture with code after review` |
| Installed console script `doc_sync` | Not Found (not on PATH; package not installed, `PackageNotFoundError`); not tried per instructions. Declared script is checked by `test_packaging.py::test_console_script_declared` (PASS) |

## 3. Requirement-to-evidence table
| Req | Status | Evidence |
|---|---|---|
| FR-1 | PASS | `test_cli.py::test_parse_args_default_cwd`; CLI runs with and without path |
| FR-2 | PASS | full-repo CLI run; `test_end_to_end.py::test_full_repo_exact_content` |
| FR-3 | PASS | title `# demo-app` and `# Not Found` in CLI runs; `test_render.py::test_full_document`, `test_all_none` |
| FR-4 | PASS | 7 `##` headings in order in full/empty/nongit/self runs; `test_embedded_headings_keep_seven_sections` |
| FR-5 | PASS | `test_precedence.py` (5 tests); full run |
| FR-6 | PASS | `test_languages.py`; `test_fs.py`; nongit run |
| FR-7 | PASS | `test_dependencies.py::test_read_dependencies_file`; full run |
| FR-8 | PASS | full run Last Commit line; `test_git_info.py::test_real_repo_with_commit` |
| FR-9 | PASS | `test_render.py::test_render_list`; CLI runs (`- item`, empty gives `Not Found`) |
| FR-10 | PASS | empty-repo CLI run; `test_not_found_value_is_exact` |
| FR-11 | PASS | `test_collect.py::test_unreadable_readme_does_not_raise`, `test_not_a_git_repo_gives_none`, `test_read_dependencies_unreadable`; nongit/empty runs |
| FR-12 | PASS | `test_collect.py::test_no_invented_values_without_usage`; self run How to Run `Not Found` |
| FR-13 | PASS | `test_entry_points.py`; full and self runs |
| FR-14 | PASS | `test_readme.py::test_section_body_*`; full run (found) and self run (`Not Found`) |
| FR-15 | PASS | `test_precedence.py::test_pyproject_wins`, `test_description_from_pyproject_name_from_readme` |
| FR-16 | PASS | `test_precedence.py::test_name_from_pyproject_description_from_readme` |
| FR-17 | PASS | `test_cli.py::test_default_cwd`, `test_empty_path_is_not_cwd` |
| FR-18 | PASS | `test_writer.py::test_creates_docs_dir`; CLI runs created `docs/` |
| FR-19 | PASS | `test_git_info.py::test_run_git_call_shape`; full run date `2026-11-18` |
| FR-20 | PASS | `test_languages.py::test_table_matches_architecture`, `test_sorted_alphabetically`, `test_unique`; self run |
| FR-21 | PASS | `test_writer.py::test_overwrites_existing`; second full run overwrote |
| FR-22 | PASS | exit 0 for empty and nongit runs |
| FR-23 | PASS | missing-path run exit 2, nothing written; `test_cli.py::test_missing_path` |
| FR-24 | PASS | file-path run exit 2 with exact message; `test_cli.py::test_file_path` |
| FR-25 | PASS | docs-is-file run exit 1, one line; `test_cli.py::test_write_failure`; `test_writer.py::test_docs_is_file`, `test_target_is_directory_no_temp_left`, `test_existing_unchanged_when_replace_fails` |
| FR-26 | PASS | full run (no fake creds); `test_dependencies.py::test_user_pass_removed`, `test_token_removed_from_direct_reference`, `test_url_query_removed`, `test_option_lines_skipped`, `test_inline_comment_stripped` |
| FR-27 | PASS | full and self runs; `test_git_info.py::test_last_commit_rejects_bad`, `test_last_commit_none_when_not_top_level`, `test_real_subfolder_of_repo` |
| FR-28 | PASS | `test_render.py::test_name_cannot_create_headings`, `test_safe_body_neutralizes_hidden_headings`; `test_readme.py::test_heading_in_fence_ignored`; `test_readme.py::test_load_bom_dropped`; `test_end_to_end.py::test_readme_headings_and_fences_keep_seven_sections` |
| NFR-1 | PASS | `test_annotations.py::test_all_signatures_annotated`; `test_packaging.py::test_python_requirement`; run on 3.11.9 |
| NFR-2 | PASS | no-leak grep over files/stdout/stderr; `test_no_fake_credentials_anywhere`, `test_secret_env_never_leaks`, `test_cli.py::test_output_has_no_env_values` |
| NFR-3 | PASS (limited) | no credential is needed by the tool; no reads of secrets found in tested behaviour (not separately tested; code inspection not performed) |
| NFR-4 | PASS | 257 tests cover FR-11, FR-23, FR-24, FR-25 failure modes (see above) |
| NFR-5 | Not Found | Not measured by tests or commands in this step; see `docs/code-review.md` |
| NFR-6 | PASS | `test_two_runs_are_byte_identical`, `test_writer.py::test_identical_on_rerun`; `cmp` identical on real second run |
| OI-7 | Not implemented (by design) | Only `.git` excluded |

Totals: FR 28 PASS, 0 FAIL; NFR 5 PASS, 0 FAIL, 1 Not Found (NFR-5, not verified here).

## 4. Defects
None found. Notes (not defects): skipped POSIX tests are unverified on this platform; the console script was not verified by execution.
