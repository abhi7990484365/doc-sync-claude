# Verification Report: SCRUM-101 Add a New Employee (Step 7)

Branch: `feature/doc-sync-claude`, HEAD `f43ffb0` (working tree clean before this report). Python 3.11.9, `.venv` of the repository. Unknown = `Not Found`.
Note: this file intentionally replaces the earlier doc_sync verification content (recoverable from git history).
Input name differences: the architecture is `docs/architecture.md` (Revision 3), the source is `src/employee_app/`. `docs/PROJECT_DOC.md` and `src/doc_sync/` do not exist in this tree and are not part of SCRUM-101 (NOT APPLICABLE; not invented).

## 1. Verdict

**VERIFIED_WITH_LIMITATIONS.** The full suite passes (441 passed, 0 failed, 0 skipped), every FR, NFR and AC has at least one executed test or an explicit Not Run / Not Covered mark, and direct spot checks of the running app agree with the requirements. No defect was confirmed. The limitations are non-blocking: manual four-browser check, deployment target, interactive `create-user`, real-load performance, network file system and non-Windows platforms were not run; department names and deployment target remain `Not Found`; there is no lock file for transitive dependencies.

## 2. Scope

Code: `src/employee_app/` against `docs/requirements.md` (FR-1 to FR-18, NFR-1 to NFR-5, AC-01 to AC-17), design-review conditions and code-review conditions. Documentation: README run/install, consistency of `docs/*.md`, `Not Found` convention, secrets, `.gitignore`. No source, test or existing doc was modified.

## 3. Commands executed and actual results

| Command (repo root unless stated) | Result |
|---|---|
| `.venv/Scripts/python -m pytest -q` | 441 passed, 0 failed, 0 skipped, 42.03 s |
| `.venv/Scripts/python -m pytest -q -m "not informative"` | 439 passed, 2 deselected (the two `informative` perf tests), 41.29 s |
| `.venv/Scripts/python -m pytest -q -rs tests/test_perf_smoke.py tests/test_e2e_add_employee.py tests/test_unlock_integration.py tests/test_lockout_concurrency.py tests/test_duplicate_race.py` | 56 passed, 14.22 s, no skip reported |
| `.venv/Scripts/python -m pytest --collect-only -q` (names only, to build the matrix) | collected; names used below |
| `.venv/Scripts/employee-admin --help` | Lists create-user, deactivate-user, init-db, unlock-user (matches README) |
| `.venv/Scripts/python -I <temp script>` (script and its database were in a temp directory outside the repo; Flask test client, throw-away generated password, fake signing key; both removed afterwards) | Section 6 |
| `git status --short` before and after the runs | empty both times (no stray db or egg-info files tracked) |

Integration marker: none exists; only `informative` is registered in `pytest.ini`. Integration-style tests are identified by file (`test_e2e_add_employee.py`, `test_auth_integration.py`, `test_unlock_integration.py`, `test_lockout_concurrency.py`, `test_duplicate_race.py`, `test_atomicity.py`, `test_account_scenarios.py`). All passed within the full run. Failed: none. Skipped: none. Flakiness repeats (5 runs) were not repeated here: Not Run.

## 4. Traceability matrix

Result column = observed in the full run of section 3 (all listed tests PASS) unless marked. File names are under `tests/`.

### Functional requirements

| Id | Tests that exercise it | Result |
|---|---|---|
| FR-1 | `test_e2e_add_employee::test_ac01_p1_form_shows_seven_fields`; `test_employee_routes::test_page_is_not_reachable_without_login`; `test_auth_integration::test_n7_unauthenticated_get_redirects_to_login` | PASS |
| FR-2 | `test_e2e_add_employee::test_ac01_p1_form_shows_seven_fields`; `test_templates::test_form_has_seven_inputs_dropdown_csrf_field_and_logout_form`; `test_employee_routes::test_get_shows_the_form_with_seven_fields_and_the_department_list` | PASS |
| FR-3 | `test_e2e_add_employee::test_ac03_n1_n2_each_empty_field_is_an_error`, `test_n1_all_empty_form_shows_seven_errors`; `test_validation_text::test_empty_or_whitespace_only_is_required_error`; `test_validation_employee::test_all_empty_form_gives_seven_errors` | PASS |
| FR-4 | `test_validation_email::test_invalid_emails_rejected`, `test_valid_emails`, `test_254_characters_accepted_and_255_rejected`, `test_leading_and_trailing_whitespace_is_trimmed`; `test_e2e_add_employee::test_ac04_n3_invalid_email`, `test_p12_n18_email_length_boundaries` | PASS |
| FR-5 | `test_e2e_add_employee::test_ac05_n4_duplicate_email`, `test_ac05b_n4b_case_only_duplicate_email`; `test_validation_email::test_case_pair_normalises_equal`; `test_db_schema::test_duplicate_email_normalized_rejected`; `test_duplicate_race::test_same_email_race_loser_sees_email_in_use`, `test_case_only_race_loser_sees_email_in_use` | PASS |
| FR-6 | `test_validation_phone::test_valid_phone_stores_ten_digits`, `test_invalid_phone_rejected`; `test_e2e_add_employee::test_ac06_n5_invalid_phone`, `test_ac06b_phone_with_parentheses_is_accepted`, `test_p3_p6_valid_phone_formats_store_ten_digits` | PASS |
| FR-7 | `test_validation_date_dept::test_today_and_tomorrow_accepted`, `test_yesterday_rejected`, `test_far_future_accepted_without_maximum`; `test_e2e_add_employee::test_ac07_n6_yesterday_rejected`, `test_ac07b_p5_p13_today_tomorrow_and_far_future_accepted`; `test_employee_service::test_past_joining_date_uses_the_clock` | PASS |
| FR-8 | `test_employee_service::test_valid_creation_writes_employee_and_audit`; `test_db_employee_write::test_successful_write_creates_one_employee_and_one_audit_row`; `test_e2e_add_employee::test_ac02_p2_to_p4_valid_creation_stores_trimmed_normalised_values` | PASS |
| FR-9 | `test_e2e_add_employee::test_ac09_p8_stay_on_a_cleared_form_with_a_message`; `test_employee_routes::test_success_redirects_with_303_to_an_empty_form_and_one_time_message`, `test_refresh_after_success_does_not_resubmit` | PASS |
| FR-10 | `test_employee_routes::test_invalid_form_returns_200_with_every_error_and_entered_values`; `test_e2e_add_employee::test_n10_several_errors_are_shown_at_once_and_values_kept`; `test_validation_employee::test_several_simultaneous_errors_are_all_reported` | PASS. Message wording is `Not Found` in requirements, so wording is not verified against a spec |
| FR-11 | `test_e2e_add_employee::test_p7_each_dropdown_choice_is_accepted`; `test_employee_routes::test_department_outside_the_list_is_rejected`; `test_validation_date_dept::test_department_in_list_accepted`, `test_department_outside_list_rejected`; startup refusal of an empty list: `test_app_startup::test_empty_department_list_fails_outside_tests` | PASS with test names "Test Dept A/B"; real department names `Not Found` |
| FR-12 | `test_cmd_create_user.*` (8 tests); `test_cmd_deactivate_user.*` (4); `test_commands_context.*`; `test_account_scenarios::test_ac11_p10...`, `test_ac12...` | PASS. Interactive hidden prompt: Not Run (section 7) |
| FR-13 | `test_e2e_add_employee::test_ac10_p9_one_audit_row_on_success_with_creator_and_time`, `test_n11_no_audit_row_on_any_rejection`; `test_atomicity::*` (6); `test_db_employee_write::test_audit_insert_failure_leaves_no_employee` | PASS |
| FR-14 | `test_logout::*` (7); `test_account_scenarios::test_ac15_p11_logout_ends_the_session`, `test_ac15_n15_n16_logout_without_token_fails_and_get_does_nothing`; `test_errors_headers::test_get_logout_is_405_page_and_does_not_log_out` | PASS |
| FR-15 | `test_validation_text::test_boundary_lengths_accepted`, `test_101_characters_rejected`, `test_length_counted_after_trim`; `test_e2e_add_employee::test_p12_n18_name_length_boundaries`; `test_errors_headers::test_body_over_16_kb_gives_413_page`, `test_body_over_16_kb_unauthenticated_is_still_401` | PASS |
| FR-16 | `test_login_lockout::*` (9); `test_db_lockout::*`; `test_login::test_unknown_user_wrong_secret_and_inactive_are_identical`; `test_validation_employee::test_password_rule`; `test_cmd_create_user::test_weak_or_empty_password_rejected`; `test_lockout_concurrency::*` (4); `test_lockout_fail_closed::*` (5) | PASS |
| FR-17 | `test_e2e_add_employee::test_n19_resubmitting_the_same_data_shows_the_duplicate_error`; `test_employee_service::test_resubmission_shows_the_duplicate_error` | PASS |
| FR-18 | `test_cmd_unlock_user::*` (6); `test_unlock_integration::*` (5); `test_db_lockout::test_unlock_clears_both_fields_and_nothing_else`, `test_unlock_unknown_id_changes_nothing` | PASS |

### Non-functional requirements

| Id | Tests / checks | Result |
|---|---|---|
| NFR-1 | `test_auth_integration::test_n7...`, `test_n8_unauthenticated_post_with_and_without_token_is_401_and_counts_unchanged`, `test_wrong_role_is_403_on_page_and_submission`; `test_auth_csrf::*`; spot check section 6 | PASS |
| NFR-2 (access control only) | `test_auth_integration::test_wrong_role_is_403_on_page_and_submission`; `test_security::test_password_hash_is_never_rendered_or_returned`; no web read route for employees exists (only `GET/POST /employees/new`, per `test_db_schema::test_no_update_or_delete_api_for_employees_or_audit` and the route list) | PASS for what is specified. Retention and PII rules `Not Found`; encryption at rest not required |
| NFR-3 (3 s) | `test_perf_smoke::test_single_submission_completes_well_within_three_seconds` (marker `informative`, passed in the full run) | PASS for a single local submission only. "Normal operating conditions" is `Not Found`; real-load performance NOT RUN |
| NFR-4 (graceful errors) | `test_atomicity::*`; `test_employee_routes::test_storage_failure_gives_generic_500_page`; `test_errors_headers::test_unhandled_exception_gives_generic_500_page`; `test_security::test_error_pages_contain_no_stack_text`; `test_lockout_fail_closed::*`; `test_app_startup::test_unreachable_database_fails_startup` | PASS |
| NFR-5 (four desktop browsers) | `test_templates::test_page_works_without_script_the_form_posts_normally`, `test_no_inline_script_and_only_same_origin_assets` (markup checks only) | NOT RUN for Chrome, Edge, Firefox, Safari (TASK-046 manual check). Markup tests do not prove browser behaviour |

### Acceptance criteria

| Id | Tests | Result |
|---|---|---|
| AC-01 | `test_e2e_add_employee::test_ac01_p1_form_shows_seven_fields` | PASS |
| AC-02 | `test_e2e_add_employee::test_ac02_p2_to_p4_valid_creation_stores_trimmed_normalised_values` | PASS |
| AC-03 | `test_ac03_n1_n2_each_empty_field_is_an_error`, `test_n1_all_empty_form_shows_seven_errors` | PASS |
| AC-04 | `test_ac04_n3_invalid_email` | PASS |
| AC-05 | `test_ac05_n4_duplicate_email` | PASS |
| AC-05b | `test_ac05b_n4b_case_only_duplicate_email`; spot check | PASS |
| AC-06 | `test_ac06_n5_invalid_phone` (includes "+" prefix case via `test_validation_phone::test_invalid_phone_rejected`) | PASS |
| AC-06b | `test_ac06b_phone_with_parentheses_is_accepted`; spot check | PASS |
| AC-07 | `test_ac07_n6_yesterday_rejected`; spot check | PASS |
| AC-07b | `test_ac07b_p5_p13_today_tomorrow_and_far_future_accepted`; spot check | PASS |
| AC-08 | `test_auth_integration::test_n7_unauthenticated_get_redirects_to_login`; spot check | PASS |
| AC-08b | `test_auth_integration::test_n8_unauthenticated_post_with_and_without_token_is_401_and_counts_unchanged`; `test_auth_csrf::test_unauthenticated_post_without_token_is_401`, `test_unauthenticated_post_with_a_valid_token_is_still_401`; spot check | PASS |
| AC-09 | `test_ac09_p8_stay_on_a_cleared_form_with_a_message`; spot check | PASS |
| AC-10 | `test_ac10_p9_one_audit_row_on_success_with_creator_and_time`, `test_n11_no_audit_row_on_any_rejection`; spot check | PASS |
| AC-11 | `test_account_scenarios::test_ac11_p10_operator_created_account_logs_in_and_sees_the_form`; `test_login::test_account_created_through_the_command_path_logs_in_and_opens_the_form` | PASS (account created through the command code path, not the interactive prompt) |
| AC-12 | `test_account_scenarios::test_ac12_n12_deactivated_account_is_rejected_at_login`, `test_ac12_open_session_of_a_deactivated_account_is_rejected_on_its_next_request` | PASS |
| AC-13 | `test_account_scenarios::test_ac13_n13_one_generic_message_for_every_cause`; `test_login::test_failure_does_not_reveal_which_part_was_wrong`; `test_login_lockout::test_locked_response_is_identical_to_wrong_credentials` | PASS |
| AC-14 | `test_account_scenarios::test_ac14_n14_lockout_cycle_with_replaced_clock`; `test_login_lockout::test_fifth_failure_locks_and_correct_value_is_rejected_for_15_minutes`; spot check | PASS |
| AC-15 | `test_account_scenarios::test_ac15_p11_logout_ends_the_session`, `test_ac15_n15_n16...`; `test_auth_integration::test_n15_after_logout_a_direct_submission_is_rejected`; spot check | PASS |
| AC-16 | `test_unlock_integration::test_a_after_unlock_the_correct_password_logs_in_ac16_p14` | PASS |
| AC-17 | `test_unlock_integration::test_b_password_hash_is_identical_before_and_after_unlock_ac17`; `test_cmd_unlock_user::test_unlocked_account_is_unchanged_including_flags_hash_and_version`, `test_second_run_gives_the_same_result` | PASS |

Other requirement scenarios: N-20 `test_unlock_integration::test_c_deactivated_and_locked_account_stays_blocked_after_unlock_n20` PASS; E-18 `test_unlock_integration::test_e18_unknown_username_changes_nothing` and `test_cmd_unlock_user::test_unknown_username_exits_non_zero_and_changes_no_row` PASS; E-8 duplicate race PASS; E-12 `test_e12_expired_session_then_submit_is_401` PASS; E-11 `test_e11_impossible_date_is_a_field_error` PASS; N-9 atomicity tests PASS.
Not Covered: E-10 (user told which date applies, `Not Found`), E-13 (over-3-s behaviour, `Not Found`), E-14 and E-15 (expected behaviour `Not Found`; atomicity makes the first case all-or-nothing, tested by `test_atomicity`), E-4 whitespace-padded email is covered by `test_leading_and_trailing_whitespace_is_trimmed`. There is no automated FR/NFR/AC traceability script (TASK-041 not written); this matrix was built by hand from test names and was not mechanically cross-checked.

## 5. Regression and negative/boundary coverage

Regression: the whole suite (441) was re-run on the committed tree and passes; the delta from the review fixes (signing key minimum, packaging) is covered by `test_app_startup::test_signing_key_minimum_length_is_enforced` and the install check below. Boundary and negative cases exist for name lengths 1/100/101, email 254/255, phone 9/10/11 digits and "+", date yesterday/today/tomorrow, 16 KB body, session lifetime edges, lock expiry edge, missing database, empty database, missing signing key, empty department list, corrupt/unreachable database. Missing files: `test_config::test_settings_file_missing_or_not_json_fails_without_leaking_path`. Empty repository does not apply to this app; the empty-database case is `test_app_startup::test_empty_database_fails_startup_naming_tables`.

## 6. Spot checks against the running app (observed output only)

Fresh temporary SQLite database, Flask test client, server date 2026-11-20, two users created in the script, generated password. Output lines as printed:

| Check | Observed |
|---|---|
| Unauthenticated `GET /employees/new` | 302, Location `/login` |
| Unauthenticated `POST /employees/new` without token | 401 |
| Unauthenticated `POST` with a valid login-page token | 401; employee rows afterwards: 0 |
| 5 wrong logins for `admin2` | each returned 200 (login page); stored failed count 5 and a `locked_until` 15 minutes after the 5th failure |
| Correct password for `admin2` after the 5 failures | 200 (login page again), no `Location` header (not logged in) |
| `admin1` login | 303 to `/employees/new` |
| Create with joining date = today and phone `555 123-4567` | 303 to `/employees/new`; page then contained the success text and the first-name field was empty (`value="Ann"` absent); one employee row (phone stored `5551234567`, date 2026-11-20) and one audit row (employee 1, creator user 1, created_at present) |
| Same email with different case (`Ann@Example.COM`) | 200, "in use" text present |
| Joining date yesterday | 200, "past" text present |
| Phone `(555) 123-4567` | 303 (accepted); stored `5551234567` |
| Phone `+1 555 123 4567` | 200 (rejected) |
| Final counts | employee 2, audit_record 2 (rejected submissions added none) |
| `POST /logout` with token; then `GET /employees/new`; `GET /logout` | 303; 302; 405 |

Not compared in the spot check: the exact text of the generic login message across causes (my check printed no value); that is covered by the AC-13 tests. Log lines printed by the app during the run contained user ids and categories only (no username, password or employee value seen).

## 7. Documentation quality

| Check | Result |
|---|---|
| README "Run and install" vs real CLI | PASS. `employee-admin --help` lists exactly init-db, create-user, deactivate-user, unlock-user; environment names match `config.py`/`app.py` (`EMPLOYEE_APP_DB_PATH`, `_SECRET_KEY`, `_ENV`, `_COOKIE_SECURE`, `_SETTINGS_FILE`); installed versions match `requirements.txt` pins (Flask 3.1.3, Flask-Login 0.6.3, Flask-WTF 1.3.0, SQLAlchemy 2.0.58, Werkzeug 3.1.9, click 8.5.1) and pytest 9.2.0 matches `requirements-dev.txt`. `pip install -e .`, `flask --app ... run` and `pip-audit` were not re-run by me: NOT RUN (pip-audit is not installed in the venv; its earlier result is recorded in `docs/code-review.md` section 8, not reproduced here) |
| `.gitignore` | PASS: covers `.env`, `.env.*` (keeps `!.env.example`), `*.db`, `*.sqlite*`, `*-wal`, `*-shm`, `*.egg-info/`, `.venv/` |
| Secrets in repo | PASS. A regex search for credential-like assignments in `src`, `tests`, `docs`, README, `pyproject.toml`, `.claude/settings.json` and `.mcp.json` found only the environment variable NAME constant, message strings and test fakes labelled as such (`fake-signing-key-for-tests-only-...`, `fake-key-should-not-be-printed`, `short-pw-x`). No tracked `.env` or database file (`git ls-files` shows only `.claude/settings.json`, `.vscode/settings.json`, `tests/test_lib_sqlite.py` by name match). The search was limited to those patterns; it is not a full secret scan (no scanner was run) |
| `Not Found` convention | PASS. Non-exact variants found only in `docs/architecture.md:456` ("Not found", a technical lookup outcome, not an unknown-marker) and `docs/code-review.md` (`NOT_FOUND`, a code constant name). `docs/ops-notes.md` marks unknowns with exact `Not Found` (also asserted by `test_perf_smoke::test_operator_notes_exist_and_mark_unknowns_exactly`) |
| Cross-document consistency | PASS with minor notes. 436 (before fixes) and 441 (after fixes) test counts agree across state, implementation report and code review; my run gives 441. Open items agree (TASK-041/044/045/046, department names, deployment target). Minor inconsistencies, none blocking: (a) `docs/implementation-report.md` section 4 says `pyproject.toml`, README were not changed, section 8 says they were (section 8 supersedes it); (b) `docs/code-review.md` section 8 says the fixes were uncommitted, they are now committed (HEAD history); (c) `.claude/rules/*.md` and the verification skill say branch `feature/doc-sync` and `src/doc_sync/`, CLAUDE.md says `feature/doc-sync-claude` and `src/employee_app/` (the work is on the latter) |
| Final `PROJECT_DOC.md` | NOT APPLICABLE / missing: `docs/PROJECT_DOC.md` does not exist and is not a deliverable of SCRUM-101 (the doc_sync CLI is absent from the tree); no content was invented |
| Markdown structure of this report | Tables and headings checked by reading; no linter was run |

## 8. Failed checks, blockers, defects

- Failed checks: none.
- Blockers: none.
- Confirmed defects: none.
- Possible risks (not defects): strict `Referer` requirement over HTTPS (Flask-WTF) to be checked on the deployment target; production app refuses to start until department names are supplied (by design); traceability matrix is manual; concurrency evidence is from one local Windows machine; code-review items REVIEW-005 to REVIEW-010 remain accepted/informational as recorded there.

## 9. Not Run, with reasons

| Check | Reason |
|---|---|
| Manual four-browser check (Chrome, Edge, Firefox, Safari), TASK-046, NFR-5 | Needs a person and real browsers |
| Deployment-target checks, production server, HTTPS termination (TASK-045) | Deployment target is `Not Found` |
| Interactive `create-user` prompt | Hidden prompt needs an interactive console; the same code path is covered through `create_account` tests only |
| Performance under real load / "normal operating conditions" (NFR-3) | Load definition is `Not Found`; only the single-request smoke test ran |
| Network file system, non-Windows platforms | Not available |
| Running the development server (`flask run`), `pip install -e .`, `pip-audit` | Not re-run in this step; earlier results are in `docs/implementation-report.md` section 8 and `docs/code-review.md` section 8 |
| Repeated (flakiness) runs of the concurrency tests | Not repeated in this step |
| Lock file for transitive dependencies | Does not exist (`Not Found`) |

## 10. Known limitations and human decisions

- Department names (`Not Found`) and deployment target (`Not Found`) must be supplied by a human before release.
- Decision: lock/constraints file for transitive dependencies (REVIEW-003 residual).
- Decision: person to perform and record the browser check (TASK-046).
- Decision: whether the README/CHANGELOG are final for the PR step; and which branch name the rule files should name (see 7).
- Defaults adopted by delegation (limits, lockout, logout, repeated submit) have no written sign-off record (`Not Found`).

## 11. Cleanup and repository state

Temporary script and database were created under the system temp directory only and removed (confirmed by listing). `git status --short` after the runs showed no changes before this report was written; the only change is `docs/verification-report.md`. `docs/sdlc-state.md` was not touched. Nothing was committed or pushed.
