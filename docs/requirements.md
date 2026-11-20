# Requirements: SCRUM-101 Add a New Employee

Source: `docs/user-story.md`
Status: APPROVED 2026-11-20 with open questions remaining as `Not Found` (see section 10).
Note: Replaces the previous doc_sync CLI requirements by user decision. Missing data is written as exactly `Not Found`.
Change log: 2026-11-20 revision after design review (DR-01, DR-02, DR-10, DR-13, DR-16, DR-17): recorded defaults adopted by user delegation ("use your recommended defaults for all of them") for OQ-10, OQ-11, OQ-14/OQ-15/OQ-17 (FR-12, FR-16, AC-11 to AC-15), logout (FR-14) and repeated submit (FR-17). Items marked "Default" are NOT stakeholder-specified values and may be changed later. Approval status unchanged.
Revision log: 2026-11-20 (user-approved "Fix and continue"): added operator-run `unlock-user` command (FR-18, extends FR-12), AC-16, AC-17, scenarios P-14, P-15, N-20, E-18 and OQ-19. This is a user-approved addition, not in the original story.

## 1. Business Objective
- BO-1: HR Administrators can register new employees with personal and employment details so that employee information is maintained centrally instead of manually (story: Business Context).

## 2. Scope

### In Scope
- An Add Employee form accessible to authenticated HR Administrators.
- Validation of the submitted data and creation of an employee record.
- Success and validation/error messages.
- User-confirmed scope addition (OQ-14, round 3; not listed in the story): the login screen and HR Administrator accounts/user management. Scope of user management is limited by a default (see FR-12): an operator-run server-side command, no web screen. Remaining details (other roles, session timeout, other password rules) are open (OQ-15, OQ-16).
- Logout action (default, FR-14).
- Audit record of who created each employee and when (OQ-13, round 3).

### Out of Scope (per story)
The story's out-of-scope list is unchanged by the user's answers. Note that login and user management are now in scope (above), although the story does not mention them.
- Edit employee details.
- Delete employee records.
- Bulk employee import.
- Employee payroll processing.

### Dependencies and Constraints
- Authentication: HR Administrators sign in with a login form (username/password session login) (confirmed, OQ-6). Building the login screen and HR Administrator accounts/user management is in scope (user-confirmed, OQ-14); defaults for account management, login security and logout are recorded in FR-12, FR-14 and FR-16 (default adopted by user delegation, 2026-11-20, not a stakeholder-specified value). Roles other than HR Administrator: Not Found (OQ-16).
- Storage technology: Not Found.
- Security of stored data: access control only, role-based, so that only authorised roles can read the data (confirmed, OQ-7).
- Implementation: a Python 3.11 web application with a browser form (confirmed, OQ-5). Web framework: Not Found (for the architecture step). Note: the project CLAUDE.md describes a Python CLI; the user confirmed the web app direction for this story.
- Supported browsers: current (latest stable) desktop Chrome, Edge, Firefox and Safari (confirmed, OQ-3).
- "Today" for date validation is the server's date/timezone (confirmed, OQ-4).
- Department list: a fixed list selected from a dropdown (confirmed, OQ-2). Department names: Not Found.

## 3. Functional Requirements
- FR-1: HR Administrators can access the Add Employee form. (story FR 1)
- FR-2: The form contains First Name, Last Name, Email Address, Phone Number, Department, Job Title and Joining Date. (story FR 2)
- FR-3: All fields are mandatory. (story FR 3) Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): a whitespace-only value counts as empty and gives the empty-field error.
- FR-4: Email must have a valid format: a standard basic local@domain.tld check. (story FR 4; OQ-9 confirmed) Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): email maximum length is 254 characters.
- FR-5: Email must be unique, compared case-insensitively. (story FR 4; OQ-1 confirmed)
- FR-6: Phone number must contain exactly 10 digits. Spaces, dashes and parentheses are stripped before counting; exactly 10 digits must remain. A "+" prefix or country code is rejected. (story FR 5; OQ-8 confirmed)
- FR-7: Joining date cannot be in the past. "Past" means before today; today is allowed. "Today" is the server's date/timezone. (story FR 6; OQ-4 confirmed) Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): there is no maximum; any valid date from today onward is accepted (OQ-10).
- FR-8: A valid submission creates an employee record. (story FR 7)
- FR-9: A success message is displayed after successful creation. After success the user stays on the Add Employee form, the form is cleared, and the success message is shown. (story FR 8; OQ-13 confirmed)
- FR-10: An invalid submission displays appropriate validation messages. (story FR 9) Message wording: Not Found.
- FR-11: Department is selected from a fixed list presented as a dropdown. (OQ-2 confirmed) The department names in the list: Not Found (not supplied by the user).
- FR-12: The system provides a login screen and HR Administrator accounts/user management. (user-confirmed scope addition, OQ-14; not in the story) Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): user management is limited to an operator-run server-side command that creates an HR Administrator account and deactivates one. There is no web screen for user management. Passwords are never taken from environment variables and never stored in plain text. Unlocking an account is specified in FR-18 (user-approved addition). Other account operations (for example password reset) and roles other than HR Administrator: Not Found (OQ-16, OQ-17, OQ-19).
- FR-13: When an employee is created, the system records which HR Administrator created the employee and when. (user-confirmed, OQ-13; not in the story) Audit retention, format and where it is viewed: Not Found (OQ-18).
- FR-14: A logout action is provided: a POST request that is CSRF-protected. After logout the user cannot access the Add Employee form. (Default adopted by user delegation, 2026-11-20, not a stakeholder-specified value.)
- FR-15: Input limits. Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): First Name, Last Name and Job Title must be 1 to 100 characters after trimming; request body is at most 16 KB. Allowed characters: Not Found. (OQ-11)
- FR-16: Login security. Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): after 5 consecutive failed logins for an account, further logins for that account are rejected for 15 minutes; login failures show one generic message that does not reveal whether the username exists; minimum password length is 12 characters, the password must not be empty, and there are no composition rules. Session timeout and any other password rules: Not Found (OQ-15).
- FR-18: Unlock command (extends FR-12). User-approved addition on 2026-11-20 ("Fix and continue"), not in the original story. An operator-run `unlock-user` command clears the failed-login count and the lock for an existing HR Administrator account. It is idempotent. It does not change the account's is_active state or its password. Behaviour for a username that does not exist: Not Found. Reactivation of a deactivated account, password reset and a forgotten-password procedure: Not Found (OQ-19).
- FR-17: Repeated submit. Default (adopted by user delegation, 2026-11-20, not a stakeholder-specified value): resubmitting the same data shows the normal duplicate-email error; no idempotency mechanism is required.

## 4. Non-Functional Requirements
- NFR-1: Only authenticated HR Administrators can add employees. Authentication is a login form (username/password session login). Unauthenticated requests to the Add Employee page are redirected to the login page; unauthenticated direct submissions are rejected with 401/403 and create no record. (story NFR 1; OQ-6 confirmed)
- NFR-2: Employee information must be stored securely. "Securely" means access control only: role-based access so that only authorised roles can read the data. (story NFR 2; OQ-7 confirmed) No encryption-at-rest requirement was stated. Retention and PII rules: Not Found.
- NFR-3: Form submission responds within 3 seconds under normal operating conditions. (story NFR 3) Definition of "normal operating conditions" (load, data volume): Not Found.
- NFR-4: Server errors are handled gracefully. (story NFR 4) Expected user-facing behaviour: Not Found.
- NFR-5: The form works on supported desktop browsers: current (latest stable) Chrome, Edge, Firefox and Safari on desktop. (story NFR 5; OQ-3 confirmed)

## 5. Acceptance Criteria

AC-01 (FR-1) Open the form
- Given I am an authenticated HR Administrator
- When I navigate to the Add Employee form
- Then the form is displayed with First Name, Last Name, Email Address, Phone Number, Department, Job Title and Joining Date fields.

AC-02 (FR-2, FR-3, FR-8, FR-9) Valid creation
- Given I am an authenticated HR Administrator on the Add Employee form
- When I submit all fields with valid values (valid unique email, 10-digit phone, non-past joining date)
- Then an employee record is created
- And a success message is displayed.

AC-09 (FR-9) After successful creation
- Given I am an authenticated HR Administrator and I submit valid employee details
- When the employee is created
- Then I remain on the Add Employee form
- And the form fields are cleared
- And the success message is shown.

AC-10 (FR-13) Audit record
- Given I am an authenticated HR Administrator
- When I successfully create an employee
- Then the system records which HR Administrator created the employee and when
- And no audit record is created for a rejected submission (derived from AC-03 to AC-08b; confirm).
- Audit retention, format and where it is viewed: Not Found (OQ-18).

AC-03 (FR-3, FR-10) Empty mandatory fields
- Given I am on the Add Employee form
- When I submit with one or more mandatory fields empty
- Then a validation error is displayed for each empty field
- And no employee record is created.

AC-04 (FR-4, FR-10) Invalid email format
- Given I am on the Add Employee form
- When I submit an email that does not have a valid format
- Then an email format error is displayed
- And no employee record is created.

AC-05 (FR-5, FR-10) Duplicate email
- Given an employee with email E already exists
- When I submit the form with email E
- Then the submission is rejected with an error stating the email is already in use
- And no new record is created.

AC-05b (FR-5) Duplicate email differing only in case
- Given an employee with email "jane.doe@example.com" already exists
- When I submit the form with "Jane.Doe@Example.com"
- Then the submission is rejected with an error stating the email is already in use
- And no new record is created.

AC-06 (FR-6, FR-10) Phone number
- Given I am on the Add Employee form
- When I submit a phone number that, after spaces, dashes and parentheses are stripped, does not contain exactly 10 digits, or that has a "+" prefix or country code
- Then a phone number error is displayed
- And no employee record is created.

AC-06b (FR-6) Formatted phone number accepted
- Given I am on the Add Employee form and all other fields are valid
- When I submit the phone number "(555) 123-4567"
- Then the phone number is accepted (10 digits remain after stripping)
- And the employee record is created with a success message.

AC-07 (FR-7, FR-10) Past joining date
- Given I am on the Add Employee form
- When I submit a joining date before today (server date)
- Then a joining date error is displayed
- And no employee record is created.

AC-07b (FR-7) Today's date accepted
- Given I am on the Add Employee form and all other fields are valid
- When I submit a joining date equal to today (server date)
- Then the joining date is accepted
- And the employee record is created with a success message.

AC-08 (FR-1, NFR-1) Unauthenticated access
- Given I am not authenticated
- When I request the Add Employee page
- Then I am redirected to the login page
- And I cannot view the form.

AC-08b (FR-1, NFR-1) Unauthenticated direct submission
- Given I am not authenticated
- When I send a direct submission of Add Employee data (bypassing the UI)
- Then the request is rejected with a 401 or 403 response
- And no employee record is created.

Acceptance criteria AC-11 to AC-15 rest on defaults adopted by user delegation (2026-11-20), not stakeholder-specified values.

AC-11 (FR-12, FR-1) Operator-created account can log in
- Given an HR Administrator account was created by the operator server-side command
- When I log in with its valid credentials
- Then the login succeeds
- And I can open the Add Employee form.

AC-12 (FR-12) Deactivated account
- Given an HR Administrator account was deactivated by the operator server-side command
- When I try to log in with its credentials
- Then the login is rejected.

AC-13 (FR-16) Wrong credentials
- Given I am on the login page
- When I submit wrong credentials
- Then the login is rejected with one generic message that does not reveal whether the username exists.

AC-14 (FR-16) Lockout
- Given an account has had 5 consecutive failed logins
- When a further login is attempted for that account
- Then the login is rejected for 15 minutes.

AC-15 (FR-14) Logout
- Given I am logged in as an HR Administrator
- When I log out (CSRF-protected POST)
- Then my session ends
- And I cannot access the Add Employee form.

AC-16 and AC-17 are for the user-approved `unlock-user` addition (FR-18, 2026-11-20).

AC-16 (FR-18) Unlock after lockout
- Given an HR Administrator account is locked after consecutive failed logins
- When the operator runs the `unlock-user` command for that account
- Then the account can log in again with the correct password.

AC-17 (FR-18) Unlock an account that is not locked
- Given an existing HR Administrator account is not locked
- When the operator runs the `unlock-user` command for that account
- Then the command succeeds
- And nothing about the account changes (including is_active and the password).

## 6. Positive Test Scenarios
- P-1 (AC-01): Authenticated HR Admin opens the form and sees all 7 fields.
- P-2 (AC-02): All fields valid and email new: record created, success message shown.
- P-3 (AC-02): Phone of exactly 10 digits is accepted.
- P-4 (AC-02): Joining date in the future (within any allowed range, see OQ-10) is accepted.
- P-5 (AC-07b): Joining date equal to today (server date) is accepted and the record is created.
- P-6 (AC-06b): A formatted phone number such as (555) 123-4567 is accepted and the record is created.
- P-7 (FR-11): Department can be chosen from the dropdown of the fixed list (names: Not Found).
- P-8 (AC-09): After successful creation the user stays on the form, the form is cleared and the success message is shown.
- P-9 (AC-10): After successful creation an audit record exists with the creating HR Administrator and the time.
- P-10 (AC-11): Account created by the operator command logs in and opens the Add Employee form.
- P-11 (AC-15): Logout via CSRF-protected POST ends the session; the form is then inaccessible.
- P-14 (AC-16): A locked account is unlocked by the operator `unlock-user` command and then logs in with the correct password.
- P-15 (AC-17): Running `unlock-user` on an account that is not locked succeeds and changes nothing; running it twice in a row gives the same result (idempotent).
- P-12 (FR-15): First Name, Last Name and Job Title of 1 and of 100 characters, and an email of 254 characters, are accepted (defaults).
- P-13 (FR-7): A joining date far in the future is accepted (default: no maximum).

## 7. Negative Test Scenarios
- N-1 (AC-03): Submit with all fields empty: an error per field.
- N-2 (AC-03): Submit with exactly one field empty, for each of the 7 fields.
- N-3 (AC-04): Email without "@", without domain, or with spaces is rejected.
- N-4 (AC-05): Email identical to an existing employee's email is rejected.
- N-4b (AC-05b): Email differing from an existing email only in letter case (for example Jane.Doe@Example.com vs jane.doe@example.com) is rejected.
- N-5 (AC-06): Phone with 9 digits, 11 digits (after stripping spaces, dashes and parentheses), letters, or empty is rejected. A phone with a "+" prefix or country code (for example +1 555 123 4567) is rejected.
- N-6 (AC-07): Joining date of yesterday or earlier is rejected.
- N-7 (AC-08): Unauthenticated request to the Add Employee page is redirected to the login page.
- N-8 (AC-08b): Unauthenticated direct submission (bypassing the UI) is rejected with 401/403 and creates no record.
- N-9 (NFR-4): Server or storage failure during submission shows a graceful error and creates no partial record.
- N-20 (FR-18): `unlock-user` on a deactivated account does not reactivate it or change its password; that account still cannot log in (derived from FR-18; confirm).
- N-12 (AC-12): Login with a deactivated account is rejected.
- N-13 (AC-13): Wrong password and unknown username give the same generic message.
- N-14 (AC-14): The 5th consecutive failure triggers lockout; a further login within 15 minutes is rejected, even with correct credentials.
- N-15 (AC-15): After logout, requesting the Add Employee page redirects to login, and a direct submission is rejected with 401/403.
- N-16 (AC-15): A logout request without a valid CSRF token is rejected; a GET request does not log out.
- N-17 (FR-16): A password under 12 characters or empty is rejected when an account is created by the operator command (interpretation of the default; confirm).
- N-18 (FR-15): A name or job title that is empty after trimming, or longer than 100 characters, is rejected; an email over 254 characters is rejected; a request body over 16 KB is rejected.
- N-19 (FR-17): Resubmitting the same data shows the normal duplicate-email error.
- N-11 (AC-10): A rejected submission (validation failure, duplicate email, unauthenticated) does not create an audit record of employee creation (derived; confirm).
- N-10 (FR-10): Multiple invalid fields in one submission: all errors are shown (whether all at once or one at a time is Not Found).

## 8. Edge Cases
- E-1: Joining date equals today (server date): accepted (OQ-4 confirmed).
- E-2: Joining date far in the future: accepted (default: no maximum, OQ-10).
- E-3: Email differing only in letter case from an existing email: rejected as duplicate (OQ-1 confirmed).
- E-4: Email with leading or trailing whitespace.
- E-5: Phone containing spaces, dashes or parentheses: separators are stripped, accepted if exactly 10 digits remain. Phone with a "+" prefix or country code: rejected (OQ-8 confirmed).
- E-6: Fields containing only whitespace: treated as empty and give the empty-field error (default).
- E-7: Very long or non-ASCII values (for example accented names) in name or job title fields. Maximum length 100 characters after trimming (default). Allowed characters: Not Found.
- E-8: Two simultaneous submissions with the same email: only one record may be created (derived from FR-5; confirm).
- E-9: Double submit (user clicks submit twice): the second submission shows the normal duplicate-email error; no idempotency mechanism (default, FR-17).
- E-10: Date at the day boundary when the user and server timezones differ: the server's date decides what "today" is (OQ-4 confirmed). Whether the user is told which date applies: Not Found.
- E-11: Invalid date values (for example 30 February) or unparseable date input.
- E-12: Session expires while the form is open, then submit: the submitter is unauthenticated, so the submission is rejected with 401/403 and creates no record (OQ-6 confirmed). Whether the entered data is preserved: Not Found.
- E-13: Response time exceeds 3 seconds (NFR-3): expected behaviour Not Found.
- E-14: Employee record is created but the audit record cannot be written (or the reverse): expected behaviour Not Found.
- E-15: After success the form is cleared; a browser refresh or back action could resubmit the data. Expected behaviour: Not Found (a resubmission of the same data would show the duplicate-email error, FR-17).
- E-16: Login attempts while locked out (15 minutes), including when the account does not exist: the generic message is the same (default; behaviour for nonexistent usernames is Not Found).
- E-18: `unlock-user` run for a username that does not exist: expected behaviour Not Found.
- E-17: Request body larger than 16 KB: rejected (default). The exact response: Not Found.

## 9. Assumptions
All items below are unconfirmed and must not be treated as final.
- A-1: "HR Administrator" is a single role that is the only role permitted to add employees (story NFR 1). Other roles: Not Found.
- A-2: Validation messages are shown to the user on the form; exact format Not Found.
- A-3: Every employee record created has the 7 listed fields only. Any additional system-generated fields (such as an employee id): Not Found.

## 10. Open Questions
Status: OQ-1, OQ-3, OQ-4, OQ-5 and OQ-9 are RESOLVED (round 1). OQ-2, OQ-6, OQ-7 and OQ-8 are RESOLVED (round 2, with the residual Not Found items noted). OQ-13 and OQ-14 are RESOLVED (round 3). OQ-10, OQ-11, OQ-15 and OQ-17 have DEFAULTS adopted by user delegation on 2026-11-20 (not stakeholder-specified values; changeable later). All others are OPEN, with answer `Not Found` until confirmed.

| Id | Question | Source | Answer |
|----|----------|--------|--------|
| OQ-1 | Is email uniqueness case-sensitive? | Story | RESOLVED: case-insensitive |
| OQ-2 | Which departments are available, and is the list fixed or managed elsewhere? | Story | RESOLVED (type): fixed list selected from a dropdown. Department names: Not Found |
| OQ-3 | Which desktop browsers (and versions) are officially supported? | Story | RESOLVED: current (latest stable) Chrome, Edge, Firefox and Safari on desktop |
| OQ-4 | What does "past" mean for the joining date: before today, or does today count? Which timezone defines "today" (user, server, company)? | Analyst | RESOLVED: past = before today; today is allowed; "today" is the server's date/timezone |
| OQ-5 | What technology and platform will implement this (web framework, UI)? CLAUDE.md describes a Python 3.11 CLI while the story describes a web form. | Analyst | RESOLVED: Python 3.11 web app with a browser form. Framework: Not Found. Storage: Not Found (both left for the architecture step) |
| OQ-6 | How are HR Administrators authenticated, and what should an unauthenticated user see (redirect, 401/403)? | Analyst | RESOLVED: login form (username/password session login). Unauthenticated page requests are redirected to the login page; unauthenticated direct submissions are rejected with 401/403 and create no record |
| OQ-7 | What does "stored securely" require (encryption at rest, access control, retention, PII rules)? Which storage technology? | Analyst | RESOLVED (security): access control only (role-based; only authorised roles can read the data). No encryption-at-rest requirement stated. Retention and PII rules: Not Found. Storage technology: Not Found |
| OQ-8 | Which characters may appear in a phone number (spaces, dashes, parentheses, "+" prefix), and are they stripped before counting digits? | Analyst | RESOLVED: spaces, dashes and parentheses are stripped before counting; exactly 10 digits must remain; a "+" prefix or country code is rejected |
| OQ-9 | What defines a valid email format (standard rule, maximum length)? | Analyst | RESOLVED (format): standard basic local@domain.tld check. Maximum length: Not Found |
| OQ-10 | Should future joining dates have a maximum allowed range? | Story | DEFAULT adopted by user delegation (2026-11-20), not a stakeholder-specified value: no maximum; any valid date from today onward |
| OQ-11 | Are there length or character limits on First Name, Last Name and Job Title? Is Job Title free text or a list? | Analyst | DEFAULT adopted by user delegation (2026-11-20), not a stakeholder-specified value: First Name, Last Name, Job Title 1 to 100 characters after trimming; email max 254; whitespace-only counts as empty; request body max 16 KB. Allowed characters and whether Job Title is free text or a list: Not Found |
| OQ-12 | Is "normal operating conditions" for the 3-second target defined (concurrent users, data volume)? | Analyst | Not Found |
| OQ-13 | Where should the user go after success (stay on form, cleared form, employee list)? Is an audit record of who created the employee required? | Analyst | RESOLVED: the user stays on the Add Employee form, the form is cleared and the success message is shown. An audit record is required of which HR Administrator created the employee and when. Audit retention, format and where it is viewed: Not Found |
| OQ-14 | Is building the login screen and user management (creating HR Administrator accounts) in scope of this story? The story does not mention it. | Analyst | RESOLVED: yes, in scope (user-confirmed scope addition). Detailed requirements: see OQ-15 to OQ-17 and FR-12 |
| OQ-15 | What are the password rules, and are there lockout, session timeout or logout requirements for the login? | Analyst | DEFAULT adopted by user delegation (2026-11-20), not a stakeholder-specified value: lockout for 15 minutes after 5 consecutive failed logins; one generic failure message; minimum password length 12, not empty, no composition rules; logout provided as a CSRF-protected POST. Session timeout and any other password rules: Not Found |
| OQ-16 | Which roles exist besides HR Administrator, and what may each role do? | Analyst | Not Found |
| OQ-17 | What user-management capabilities are required (create, disable, reset password, delete accounts) and who performs them? | Analyst | DEFAULT adopted by user delegation (2026-11-20), not a stakeholder-specified value: an operator-run server-side command creates and deactivates HR Administrator accounts; no web screen; passwords never from environment variables or stored in plain text. Other capabilities (for example password reset): Not Found |
| OQ-18 | What are the retention period, format and viewing method (who sees it, where) of the audit record? | Analyst | Not Found |
| OQ-19 | How is a deactivated account reactivated, how are passwords reset, and what is the forgotten-password procedure? (`unlock-user` covers only unlocking, FR-18.) | Analyst | Not Found |

## 11. Traceability
| Story item | Requirement | Acceptance criteria |
|------------|-------------|---------------------|
| FR 1 | FR-1 | AC-01, AC-08, AC-08b |
| FR 2 | FR-2, FR-11 | AC-01, AC-02 |
| FR 3 | FR-3 | AC-03 |
| FR 4 | FR-4, FR-5 | AC-04, AC-05, AC-05b |
| FR 5 | FR-6 | AC-06, AC-06b |
| FR 6 | FR-7 | AC-07, AC-07b |
| FR 7 | FR-8 | AC-02 |
| FR 8 | FR-9 | AC-02 |
| FR 9 | FR-10 | AC-03 to AC-07 |
| NFR 1 | NFR-1 | AC-08, AC-08b |
| FR 8 (extended by OQ-13) | FR-9 | AC-09 |
| User answer OQ-13 (not in story) | FR-13 | AC-10 |
| User answer OQ-14 (not in story) | FR-12 | AC-11, AC-12 |
| Default, OQ-15 (not in story) | FR-16 | AC-13, AC-14 |
| Default, logout (not in story) | FR-14 | AC-15 |
| User-approved addition, unlock-user (not in story) | FR-18 | AC-16, AC-17 |
| Default, OQ-11 (not in story) | FR-3, FR-4, FR-15 | AC-03 (whitespace-only), N-18 |
| Default, OQ-10 (not in story) | FR-7 | P-13, E-2 |
| Default, DR-17 (not in story) | FR-17 | N-19, E-9 |
| NFR 2 to 5 | NFR-2 to NFR-5 | No story AC (see N-9, E-13 for derived scenarios) |

## 12. Approval
- Status: APPROVED by the user with open questions left as `Not Found` (OQ-2 department names, OQ-12, OQ-16, OQ-18 and the E-14/E-15 behaviours). Revision 2026-11-20 added defaults adopted by user delegation (OQ-10, OQ-11, OQ-15, OQ-17, logout, repeated submit); these are not stakeholder-specified values and may be changed later. The approval metadata below is unchanged.
- Approved by: User (human reviewer)
- Approval date: 2026-11-20
