# Design Review: SCRUM-101 Add a New Employee

Note: Replaces the previous doc_sync CLI design review by user decision. Nothing is carried over.
Convention: a "Finding" is something observed in the documents (evidence cited). A "Recommendation" is the reviewer's suggestion and is not an approved change. Unknown = `Not Found`.

## 1. Review Overview

| Item | Value |
|---|---|
| Story | SCRUM-101 Add a New Employee |
| Reviewer role | Senior Software Architect / Technical Design Reviewer (independent) |
| Review date | 2026-11-20 |
| Inputs | `docs/requirements.md` (APPROVED 2026-11-20), `docs/architecture.md` (stage command calls it `architecture-design.md`; the actual file is `docs/architecture.md`) |
| Rules applied | `.claude/rules/rule-design-review.md`, `.claude/skills/design-review/SKILL.md`, `.claude/rules/architecture.md` |
| Method | Document-only review. No code, tests or running system exist, so no test or runtime evidence is claimed. |
| Documents modified | None other than this file |
| Review 1 | Sections 1 to 12 (original review of architecture Revision 1). Findings DR-01 to DR-24. Kept unchanged as the record of what was found. |
| Review 2 (re-review) | Sections 13 to 18. Re-review of architecture Revision 2 and the revised requirements (FR-12, FR-14 to FR-17, AC-11 to AC-15). Statuses of DR-01 to DR-24, findings NR-01 to NR-11. Its verdict (section 17) is SUPERSEDED by Review 3. |
| Review 3 (final re-check) | Sections 19 to 24. Re-check of architecture Revision 3 (D-24, D-25, OQ-A15, `unlock-user`) and requirements with FR-18, AC-16, AC-17, OQ-19. Statuses of NR-01 to NR-11 and residual DR-01, DR-05, DR-11, DR-12, DR-24; new findings NR-12 to NR-15. **The CURRENT verdict is in section 23.** Where earlier sections differ from sections 19 to 24, sections 19 to 24 apply. |

## 2. Scope

In scope: traceability of requirements to components, component design, data model, validation rules, error handling, security (auth ordering vs CSRF, sessions, password hashing, brute force, audit integrity, PII, secrets), testability, maintainability, technical risks, consistency between the two documents.

Out of scope: application code, implementation plans, editing `requirements.md` or `architecture.md`, approving the architecture, advancing pipeline state.

Treatment of unknowns: items that requirements leave as `Not Found` (OQ-2, OQ-10, OQ-11, OQ-12, OQ-15 to OQ-18, E-6, E-10, E-12 to E-15) are treated as open questions. They become findings only where the architecture silently assumed an answer, or where the gap creates a risk the architecture does not contain.

## 3. Review Summary

Overall the design is small, coherent and mostly well argued. Strengths (see DR-23): framework-free validation, database-enforced email uniqueness, one transaction for employee plus audit, Post/Redirect/Get, an explicit authentication-first ordering decision (D-5), and clear separation of Confirmed vs Proposal items.

Main concerns:
- Login is in scope (FR-12) but brute-force protection, password floor and user management are unresolved while the stored data is personal data (DR-01, DR-02, DR-10).
- Several security details are under-specified or internally inconsistent: CSRF/auth ordering on login routes, session claims, open redirect, `Secure` cookie behind a TLS-terminating proxy, PII in stack-trace logs (DR-04 to DR-07, DR-09).
- SQLite concurrency behaviour is described more optimistically than the design can guarantee (DR-08).
- Missing pieces: schema creation/migration and DB session lifecycle, and no enforcement of the only confirmed storage-security requirement (NFR-2) (DR-11, DR-12).
- The architecture document contradicts itself on approval status (DR-03).

Finding counts: see section 5.1 (24 findings).

## 4. Requirements Traceability

Check performed: every FR, NFR, AC from `requirements.md` against the architecture section 2 mapping and component sections.

| Requirement group | Architecture coverage | Result |
|---|---|---|
| FR-1 to FR-11 | Mapped in arch section 2 to C-2 to C-9 and section 6.5 rules | Covered |
| FR-12 (login, accounts/user management) | C-2, C-6, C-10 (CLI only) | Partially covered. "User management" reduced to a create-account command (D-11); see DR-02 |
| FR-13 audit | C-5, C-6, AuditRecord, D-7 | Covered; E-14 behaviour is a Proposal (OQ-A2) |
| NFR-1 | C-2, C-3, D-5 | Covered; ordering details incomplete (DR-04) |
| NFR-2 | C-2 role check, no read endpoint, deployment note | Covered only nominally; enforcement is outside the design (DR-12) |
| NFR-3 | Smoke check only (9.6); conditions `Not Found` (OQ-12) | Open question, handled honestly |
| NFR-4 | Error handlers, D-8, transactions | Covered; see DR-08, DR-09 |
| NFR-5 | Plain HTML5, manual check | Covered |
| AC-01 to AC-10 (incl. 05b, 06b, 07b, 08b) | All listed in arch section 2 | Covered |
| Edge cases E-1 to E-15, N-1 to N-11 | E-8, E-9, E-12, E-14, E-15, N-9 mapped; E-4 to E-7, E-11 via 6.5; N-10 via AS-5 | E-10 and E-13 not mapped to any component or test (acceptable: both `Not Found` in requirements) |

Unsupported architecture decisions (not required by requirements): the `POST /logout` route, `is_active` attribute, security response headers, 413 handling, a separate AuditRecord table. All are either flagged as Proposal or minor; see DR-16, DR-21, DR-22.

Traceability defects: dangling ids `A-5` and `A-6` (DR-14).

## 5. Review Findings

### 5.1 Count by severity

| Severity | Count | IDs |
|---|---|---|
| Critical | 0 | none |
| High | 2 | DR-01, DR-02 |
| Medium | 11 | DR-03 to DR-13 |
| Low | 9 | DR-14 to DR-22 |
| Informational | 2 | DR-23, DR-24 |
| Total | 24 | |

Status values: Open (needs action), Open - Human decision (needs a user decision), Noted.

### 5.2 Findings

#### DR-01 Login brute-force protection absent
- Category: Security
- Severity: High
- Description: Login is in scope (FR-12, OQ-14) and guards personal data, but the design has no rate limiting, throttling or lockout. This is an acknowledged gap, not a silent one.
- Evidence: arch 8.6 ("Login brute-force protection ... `Not Found`"), 12.3 first risk bullet, C-2 "Not designed ... lockout"; requirements OQ-15 `Not Found`. Flask-Login is stated to not include lockout (arch section 4).
- Impact: Credential guessing against the only authentication control. Combined with DR-10 (no password floor) the risk is higher. Exposure is "unmitigated" in the document's own words.
- Recommendation: Request a human decision. Minimum: add a technical throttle on `POST /login` (per username and per source address, configurable, with a generic response) described as a technical safeguard and not as a business lockout rule. Record the chosen option in architecture and add the matching tests to section 9.4.
- Status: Open - Human decision

#### DR-02 FR-12 "user management" reduced to an unconfirmed CLI
- Category: Requirements Traceability
- Severity: High
- Description: Requirements put "HR Administrator accounts/user management" in scope (FR-12). Architecture satisfies it with an operator command (C-10, D-11) and designs no disable, reset or delete. The architecture itself says this needs confirmation. FR-12 has no acceptance criteria, so nothing verifies the interpretation.
- Evidence: requirements FR-12, Section 11 row "OQ-14 ... None yet"; arch C-10, D-11, OQ-A1, arch 13 (OQ-A1 still open).
- Impact: If the user expects web account management, C-2, C-3, C-9 and the authorisation model change (major rework). If a CLI is acceptable, no AC currently proves FR-12 done.
- Recommendation: Obtain an explicit decision on OQ-A1/OQ-17 before implementation. Whichever is chosen, ask for at least one AC for FR-12 (for example "an account created by the chosen mechanism can log in and add an employee"). Do not widen the design until requirements are updated.
- Status: Open - Human decision

#### DR-03 Architecture document contradicts itself on approval status
- Category: Architecture Completeness (consistency between documents)
- Severity: Medium
- Description: The header says "DRAFT for design review. Not approved." Section 13 says "APPROVED by the user ... including the Proposal items D-1 to D-11 and OQ-A6, OQ-A7". Yet D-7 depends on OQ-A2 and D-11 on OQ-A1, which Section 13 also lists as still open. D-12 to D-14 are not covered by the approval statement. Section 10 states "None is approved by a human yet."
- Evidence: arch lines "Status: DRAFT", section 10 intro, section 13, D-7, D-11, OQ-A1, OQ-A2.
- Impact: Ambiguity over which Proposals are binding (for example atomic audit, CLI accounts, UTC audit time, serving/HTTPS) leads to rework or silent assumptions during implementation.
- Recommendation: Architecture owner to reconcile: state per decision id (D-1 to D-14) and per OQ-A1 to OQ-A7 whether it is approved, open or rejected, and remove the "DRAFT" line or the "APPROVED" line. This review does not edit the document.
- Status: Open - Human decision (confirm approval scope)

#### DR-04 Authentication-before-CSRF ordering is incompletely specified
- Category: Security
- Severity: Medium
- Description: D-5 correctly identifies that CSRF middleware would otherwise return 400 before the 401/403 required by AC-08b. It does not specify the behaviour for routes that are legitimately unauthenticated and state-changing (`POST /login`, and `POST /logout` for an expired session). Section 7 row "CSRF token missing or invalid" says "400 or 403", and "401 or 403" for an unauthenticated caller, leaving the status undefined. Applied literally, "authentication check first" would reject every login POST as unauthenticated.
- Evidence: arch D-5, sequence diagram 3.1, section 7 CSRF row, 8.3 ("CSRFProtect on all POST requests (login, logout, add employee)"), 6.3.
- Impact: Ambiguous behaviour that tests (9.2 "Test confirms the check ordering of D-5") cannot assert deterministically; risk of either a broken login or a CSRF bypass on a public route.
- Recommendation: Amend architecture to state an allow-list of public routes (`/login`) where CSRF is enforced without the authentication-first rule, define one status code for CSRF failure for authenticated callers (a single value, not "400 or 403"), and define the status for an unauthenticated logout. Add these cases to the 9.2 test list.
- Status: Open

#### DR-05 Session handling claims are under-specified or not meaningful
- Category: Security
- Severity: Medium
- Description: (a) "Session id regenerated at login" is stated, but the design uses Flask's signed session cookie (arch 8.1 "Signed session cookie"). A signed-cookie session has no server-side session id to regenerate unless a server-side store is added; the claim does not describe a mechanism. (b) Logout and disabled-account handling are not tied to a server-side check: the doc does not state that the user loader re-reads `is_active` and `role` on every request. (c) Flash messages (D-6) also use the session cookie. (d) Session lifetime default is `Not Found`, and the doc says "Flask's browser-session cookie behaviour applies".
- Evidence: arch 8.1, C-2, D-6 ("Needs session storage for the flash"), 6.3, User model `is_active`.
- Impact: Possible session fixation or stale-session assumptions (a stolen or old signed cookie remains valid until it expires, even after logout or disabling the account). Gap between the stated mitigation and the mechanism.
- Recommendation: Amend architecture to describe the real mechanism: either clear and re-issue the session at login and state that a signed cookie cannot be revoked server-side (accept and document), or add a server-side session store. State that every request re-loads the User and rejects inactive or wrong-role users. Set an explicit technical maximum session lifetime (configurable, not a business rule). Verify framework behaviour for these points at implementation; this review has not verified library behaviour.
- Status: Open

#### DR-06 Post-login redirect to "originally requested page" may be an open redirect
- Category: Security
- Severity: Medium
- Description: Login flow redirects "to the originally requested page or the Add Employee form". No validation of the target is specified.
- Evidence: arch 6.3 step 1; arch 8.6 lists input handling without mention of redirect targets.
- Impact: A crafted login link could send an authenticated user to an external site (phishing).
- Recommendation: Amend architecture: accept only relative, same-site paths from a fixed allow-list (or ignore the parameter and always go to the Add Employee form); add a test.
- Status: Open

#### DR-07 `Secure` cookie flag conditioned on HTTPS while TLS terminates in front of the app
- Category: Security
- Severity: Medium
- Description: C-2 and 8.1 set `Secure` "when served over HTTPS". D-14 and AS-3 place HTTPS termination in front of the application. Behind a terminating proxy the app itself sees plain HTTP unless proxy headers are trusted; the flag may then never be set. Handling of forwarded headers is not designed. Deployment target is `Not Found` (OQ-A3).
- Evidence: arch C-2, 8.1, D-14, AS-3, OQ-A3.
- Impact: Session and CSRF cookies could be sent over HTTP in a real deployment while the design claims otherwise.
- Recommendation: Amend architecture: make `Secure` a required configuration setting that is on by default and must be explicitly turned off for local development, and state whether and how forwarded headers are trusted. Mark the dependency on OQ-A3.
- Status: Open

#### DR-08 Duplicate-email race and database lock behaviour overstated
- Category: Error Handling / Data Flow
- Severity: Medium
- Description: Section 7.3 says SQLite serialises writers and the loser receives an integrity error. With SQLite a competing writer can instead hit a busy/locked condition, which section 7 maps to a generic 500 (row "Database unavailable, locked, disk full"). No busy timeout is designed. Also, C-5 is said to translate "unique violation" to the email error, but an integrity error can come from other constraints (foreign keys, not-null) and the design does not require checking which constraint failed.
- Evidence: arch 7.3, section 7 table row on locked database, C-5, C-6 Errors, 9.2 race test (patches the pre-check, so lock behaviour is not exercised), AS-11.
- Impact: E-8 and E-9 may show users a 500 error instead of "email already in use"; a different integrity failure could be misreported as a duplicate email.
- Recommendation: Amend architecture: specify a configured busy wait for the database, specify that only a violation of the `email_normalized` unique index maps to the email error and every other integrity error maps to the generic failure, and add an integration test using two real connections to a temporary file database (not in-memory).
- Status: Open

#### DR-09 Personal data can reach logs through exception text, contradicting 8.7
- Category: Security
- Severity: Medium
- Description: Section 8.7 says employee names, email and phone are not logged and stack traces are logged server-side. C-11 logs "server errors with stack trace". Database-layer exceptions commonly include the failing SQL parameters in their message (SQLAlchemy has an option to hide them). The design does not mention suppressing parameters or scrubbing exception text, and test 9.4 checks only that the password does not appear in logs.
- Evidence: arch 8.7, C-11, 9.4, section 7 (storage failure "log with stack trace").
- Impact: Names, emails and phone numbers could be written to application logs on any storage error, defeating the PII log rule. This cannot be confirmed without running the stack; it is a design gap in that no control is specified.
- Recommendation: Amend architecture to require parameter hiding on the database engine and log-scrubbing of exception messages for the employee fields, and extend 9.4 with a test that provokes a storage error with a known email and asserts the log capture does not contain it.
- Status: Open

#### DR-10 Password handling: no floor, env-var passwords, username enumeration by timing
- Category: Security
- Severity: Medium
- Description: (a) Password rules are `Not Found` and the minimum length has "no default business rule invented" (8.4), so as written an empty or one-character password could be set by C-10. (b) C-10 and C-7 allow the password through an environment variable; environment values may be visible to other processes or in shell/CI history. (c) 8.4 and C-2 promise a generic login error but do not say that a hash comparison is still performed when the user does not exist, so response time may reveal valid usernames.
- Evidence: arch 8.4, C-10, C-7 ("any initial administrator password"), C-2 Proposal, 6.4; requirements OQ-15 `Not Found`.
- Impact: Weak or empty credentials on the only gate to PII; username enumeration; credential exposure via environment.
- Recommendation: Request a decision on a technical minimum (for example reject empty and trivially short passwords) separate from the unresolved business policy; prefer interactive prompt over environment variable in C-10 and document the environment option as lower assurance; require a dummy hash check for unknown or inactive users; add tests.
- Status: Open - Human decision (password floor value)

#### DR-11 Missing components: schema creation/migration and database session lifecycle
- Category: Architecture Completeness
- Severity: Medium
- Description: No component or step creates the schema, versions it or migrates it. C-6 owns "schema, session/transaction handling" but the design does not say how sessions are scoped per request or how the schema is initialised in tests, development and production. C-10 and the app both need a ready database. The unique index on `email_normalized` (the only real uniqueness guarantee) depends on schema creation being reliable.
- Evidence: arch C-1, C-6, 6.1, section 4 (SQLAlchemy chosen without Flask-SQLAlchemy; no migration tool listed), 9.2 ("temporary SQLite database per test").
- Impact: Production database could start without the unique index or audit table; future schema change (for example OQ-11 limits) has no path; hand-rolled session handling risks leaks and inconsistent transactions.
- Recommendation: Amend architecture to define schema initialisation and versioning (either a migration tool or an explicit, tested startup step that fails fast if the schema or unique index is missing) and the per-request session lifecycle.
- Status: Open

#### DR-12 NFR-2 enforcement rests on unspecified deployment
- Category: Security / Architecture Completeness
- Severity: Medium
- Description: The only confirmed storage-security requirement is role-based access control (NFR-2). The design satisfies it because no read endpoint exists, and relies on file/server permission on the database "Proposal, outside application code". Deployment target is `Not Found`. Nothing in the design places the database file outside web-served or version-controlled paths or checks permissions.
- Evidence: arch 8.2, OQ-A3, OQ-A4, AS-4, section 4 SQLite trade-off ("file-level access control only").
- Impact: NFR-2 could be met on paper and violated in practice (database file readable by other accounts, committed to the repository, or placed under a static directory). Backup handling is also undefined (`Not Found`).
- Recommendation: Add to architecture a deployment requirement set: database location configured by environment variable, outside the static/served directory, excluded from version control, owned and readable only by the service account; consider a startup warning if permissions are broader. Treat OQ-A3 and OQ-A4 as needing human answers before implementation is signed off.
- Status: Open - Human decision (OQ-A3, OQ-A4)

#### DR-13 Unbounded field lengths and undefined request-size ceiling
- Category: Data Flow / Validation
- Severity: Medium
- Description: D-9 deliberately avoids inventing limits (consistent with OQ-11 `Not Found`) but relies on a "request body ceiling" whose value is itself undefined, and sets columns to unbounded or generous text. The email column carries the unique index, and the email maximum is `Not Found`.
- Evidence: arch D-9, section 7 ("Oversized request body ... configured technical ceiling"), 12.3 second risk bullet, C-7 (limits optional); requirements E-7, OQ-11, OQ-9.
- Impact: Very large values may be stored, break page rendering or slow responses (NFR-3); an unindexable or oversized unique key on some databases.
- Recommendation: Keep the "no invented business rule" principle but require a documented technical ceiling per field, with a stated value chosen by a human and labelled technical (not business). This is a question for the user, not an invented requirement.
- Status: Open - Human decision (ceiling values)

#### DR-14 Dangling and unmapped references in the traceability table
- Category: Requirements Traceability
- Severity: Low
- Description: Arch section 2 cites "A-6" (FR-3 row) and "A-5" (AC-03 row), and 6.5 cites "A-6". Neither exists in requirements (A-1 to A-3) or in architecture (AS-1 to AS-13; the relevant ones appear to be AS-5 and AS-6). E-10 and E-13 have no mapping or test.
- Evidence: arch section 2 rows FR-3, AC-03; 6.5 intro; requirements section 9; arch section 11.
- Impact: Traceability that points to nonexistent ids; risk that readers believe a requirement exists.
- Recommendation: Correct to AS-5/AS-6 (if that was the intent) and list E-10 and E-13 explicitly as unmapped open items.
- Status: Open

#### DR-15 Diagram and component text are inconsistent
- Category: Component Design
- Severity: Low
- Description: The diagram draws C-4 depending on C-8 and C-7 (V --> K, V --> G), while C-4 text says dependencies "none" and 9.1 says a fixed date is passed into C-4. Text says C-5 depends on C-8 and C-2 and C-10 on C-7; the diagram omits these edges (C-10 only to P). C-1 is not in the diagram. The diagram also titles the app "doc_sync web application".
- Evidence: arch section 3 diagram, C-1, C-2, C-4, C-5, C-8, C-10, 9.1.
- Impact: Misleading dependency picture; the stated "C-4 has no dependency" rule could be violated by following the diagram.
- Recommendation: Align the diagram to the text (C-5 supplies today and limits to C-4) and add C-1 and the missing edges.
- Status: Open

#### DR-16 Silent or partial assumptions in auth model
- Category: Requirements Traceability
- Severity: Low
- Description: C-2 and C-3 include `POST /logout`, while C-2 says the logout requirement is "Not designed" (OQ-15 `Not Found`). The User model carries `is_active` with no way to disable (C-10 creates only). Username uniqueness is "case-insensitive handling to be confirmed" (AS-9) but no normalised column or rule exists for usernames, unlike email.
- Evidence: arch C-2, C-3, 6.1 User, AS-9, OQ-17.
- Impact: Small inconsistencies; usernames "Admin" and "admin" could coexist or collide depending on database collation.
- Recommendation: Either state logout and `is_active` as Proposal items, or remove them until required; decide username comparison and store a normalised username with a unique index if case-insensitive.
- Status: Open - Human decision (logout inclusion, username rule)

#### DR-17 Double-submit and lost-response behaviour can hide the success message
- Category: Error Handling
- Severity: Low
- Description: 7.2 accepts that a second click returns "email already in use". The browser shows the last response, so the user may see an error for a record that was just created, which conflicts with the intent of FR-9. The optional disable-button script conflicts with the proposed restrictive CSP unless served as a static file (8.6 allows only self-hosted assets, so inline script would be blocked). If the 303 response is lost, the record exists and a retry reports a duplicate.
- Evidence: arch 7.2, C-9, 8.6, D-6; requirements E-9, E-15 `Not Found`.
- Impact: Confusing UX in an edge case; no data integrity risk.
- Recommendation: Specify that any script is a static, same-origin file; optionally define a one-time form token to make a repeated submission idempotent, or record explicitly that the confusing message is accepted.
- Status: Open - Human decision (accept or add idempotency)

#### DR-18 Validation details with Unicode and normalisation
- Category: Data Flow / Validation
- Severity: Low
- Description: AS-7 and 6.5 require ASCII digits only; a naive digit check in many languages accepts non-ASCII digits, so tests must target this explicitly. D-3/AS-8 lower-case the whole address and accept Unicode case-folding gaps, so case-only duplicates in non-ASCII text may pass uniqueness (accepted by the document). Whitespace stripping targets "spaces" only; other Unicode spaces are unspecified.
- Evidence: arch 6.5 Phone row, D-3, AS-7, AS-8; 9.1 test list (no Unicode digit case listed).
- Impact: Minor inconsistencies versus AC-05b and FR-6 for unusual input.
- Recommendation: Add test cases for non-ASCII digits and non-ASCII email case pairs; state the whitespace set to be trimmed; consider a stronger case-fold operation for the normalised email.
- Status: Open

#### DR-19 Technology and dependency observations
- Category: Technology Selection / Dependency Management
- Severity: Low
- Description: (a) "SQL portable ... by changing a URL" (section 4, D-2) is optimistic: locking behaviour, timestamp handling and error text differ per database, so the claim should read as "easier", not "by URL". (b) The stack table includes a "python-dotenv: Not used" row and a "pytest plugins: None" row, which are noise. (c) Flask-WTF is added only for CSRF and pulls WTForms that is explicitly not used. (d) No dependency pinning or vulnerability-review practice is described, and Python 3.11 compatibility of the chosen versions is not evidenced in the document. (e) The hand-assembled security stack (Flask-Login, own role check, own throttle if DR-01 is accepted) grows if OQ-15 to OQ-17 are answered; the document itself notes Django as the alternative.
- Evidence: arch section 4, D-1, D-2, D-4, 12.3.
- Impact: Limited; mostly maintainability and expectation-setting.
- Recommendation: Reword (a); delete (b); record that (c) is accepted; require pinned versions and a compatibility check against Python 3.11 at implementation; revisit the framework only if FR-12 grows beyond the CLI interpretation (decision already approved as D-1; no change proposed now).
- Status: Noted

#### DR-20 Testing architecture gaps
- Category: Testability
- Severity: Low
- Description: The testing plan is strong, but: (a) it does not state that CSRF protection is enabled in the test configuration (test clients often disable it, which would make D-5 untestable); (b) no test for a posted department outside the configured list although 6.5 defines the rule; (c) no tests for `/login` CSRF, inactive account, oversized body (413), open redirect, or `Cache-Control`/headers beyond "response headers"; (d) the NFR-3 timing smoke check can be flaky on shared machines; (e) real concurrency is "optional" (see DR-08).
- Evidence: arch 9.1 to 9.6, 6.5, section 7.
- Impact: Some designed behaviours would ship untested, contrary to the project rule that every behaviour gets a test.
- Recommendation: Add these cases to section 9; define the NFR-3 check as informative, not a gate; make the two-connection race test mandatory.
- Status: Open

#### DR-21 Hardening items not covered
- Category: Security
- Severity: Low
- Description: No guard against running with the framework debug mode in production (D-8 mentions "debug only" as the alternative); no `Cache-Control: no-store` on authenticated pages and the re-rendered form with entered personal data; no HSTS mention although HTTPS is assumed (AS-3, D-14).
- Evidence: arch D-8, 8.6, D-14, AS-3.
- Impact: Debug exposure of internals would breach NFR-4 and 8.7; cached PII in the browser history.
- Recommendation: Add startup refusal for debug mode outside development, no-store cache headers on authenticated pages, and HSTS at the TLS terminator or app.
- Status: Open

#### DR-22 Audit table integrity details
- Category: Data Model / Security
- Severity: Low
- Description: AuditRecord has no uniqueness on `employee_id` although each employee gets exactly one audit row (AC-10), no protection against alteration beyond the "no update/delete operations" convention in C-6, and references the user by id only. Audit-record creation for accounts (C-10) is not recorded (not required).
- Evidence: arch 6.1 AuditRecord, C-6, AS-10; requirements FR-13, OQ-18 `Not Found`.
- Impact: Audit integrity is convention-based; acceptable for the current requirement but easy to weaken later. A separate table is also more than the requirement strictly needs (two columns on Employee would meet FR-13), though a separate table is a defensible choice.
- Recommendation: Add a unique constraint on `employee_id`, restrict the application database account to insert-only on the audit table where the database supports it, and keep the separate-table decision as a stated trade-off pending OQ-18.
- Status: Open

#### DR-23 Design strengths confirmed (observation)
- Category: Component Design
- Severity: Informational
- Description: Verified in the documents: pure validation functions (C-4, D-4) with an injectable clock (C-8); unique index on a normalised email as the real guarantee, with a friendly pre-check (6.5, D-3); employee and audit in one transaction (7.1); Post/Redirect/Get (D-6); explicit statement of Confirmed vs Proposal; secrets from environment only (8.5, C-7); fail-fast startup (C-1, C-7); authentication check placed before CSRF to satisfy AC-08b (D-5).
- Evidence: arch sections 1.3, 5, 6.5, 7, 8.5, 10.
- Impact: None; no change required.
- Recommendation: Retain.
- Status: Noted

#### DR-24 Project rules still describe a CLI
- Category: Maintainability / Consistency
- Severity: Informational
- Description: Architecture records that `CLAUDE.md` still describes a Python CLI and `doc_sync` layout, and that the package layout is not defined here. Requirements section 2 also notes the conflict. This review did not assess `CLAUDE.md` in depth and makes no claim about its current text beyond what these two documents state.
- Evidence: arch 12.3 last bullet; requirements section 2 Dependencies and Constraints.
- Impact: Agents and reviewers may apply CLI-oriented rules (for example the PROJECT_DOC.md output) to a web application.
- Recommendation: User to decide whether to update project rules and package layout; not an architecture change.
- Status: Open - Human decision

## 6. Risk Assessment

| Risk | Likelihood / impact (from documented evidence) | Related findings | Mitigation in current design |
|---|---|---|---|
| Credential guessing on login | Documented as unmitigated; impact is access to PII entry | DR-01, DR-10 | None |
| Wrong interpretation of FR-12 | Possible major rework if web user management is expected | DR-02 | Flagged as OQ-A1 only |
| Session, redirect and cookie weaknesses | Plausible given proxy deployment and signed-cookie sessions | DR-05, DR-06, DR-07 | Partial |
| PII leaking into logs | Plausible on storage errors | DR-09 | Policy only, no control |
| Concurrency and lock errors shown as 500 | Plausible under simultaneous submissions | DR-08 | Partial (unique index) |
| NFR-2 met on paper only | Depends on deployment, which is `Not Found` | DR-12 | Proposal outside code |
| Schema/index missing in an environment | Would break FR-5 guarantee | DR-11 | None |
| Unclear approval scope | Rework or silent assumptions | DR-03 | None |
| Performance (NFR-3) | Cannot be assessed, conditions `Not Found` | (OQ-12) | Smoke check only |

## 7. Review Category Evaluation

| Category | Result | Findings |
|---|---|---|
| Requirements Traceability | Mostly complete; FR-12 partial; dangling ids | DR-02, DR-14, DR-16 |
| Architecture Completeness | Missing schema/session lifecycle and enforcement of NFR-2; approval contradiction | DR-03, DR-11, DR-12 |
| Component Design | Sound separation; diagram inconsistencies; C-1, C-8, C-11 are thin (acceptable) | DR-15, DR-22, DR-23 |
| Technology Selection | Justified with alternatives; some overstated claims | DR-19 |
| Data Flow | Clear main flow; unbounded sizes; Unicode edge cases | DR-13, DR-18 |
| Error Handling | Good table; lock/race, double submit gaps | DR-08, DR-17 |
| Security | Good baseline; several gaps | DR-01, DR-04 to DR-07, DR-09, DR-10, DR-21 |
| Testability | Strong design; plan gaps | DR-20 |
| Maintainability | Modular monolith, framework-free rules; drift in diagram and ids | DR-14, DR-15, DR-24 |
| Dependency Management | Few dependencies, mostly justified; no pinning strategy | DR-19 |

## 8. Recommendations

Recommendations are suggestions only. Items are grouped by who must act and are not an implementation plan.

Needs human decision first:
1. DR-01 brute-force approach.
2. DR-02 / OQ-A1 account management interpretation, plus acceptance criteria for FR-12.
3. DR-03 approval scope of D-1 to D-14 and OQ-A1 to OQ-A7.
4. DR-10 technical minimum password rule.
5. DR-12 / OQ-A3 / OQ-A4 deployment target and acceptance of no encryption at rest.
6. DR-13 technical size ceilings.
7. DR-16, DR-17, DR-24 smaller decisions.

Architecture amendments recommended (see section 9): DR-03 to DR-13, plus DR-14, DR-15, DR-16, DR-18, DR-21, DR-22.

Test architecture additions: DR-20 and the tests named in DR-04, DR-06, DR-08, DR-09, DR-10.

## 9. Architecture Changes Required

None of these have been applied. Each needs human approval before `docs/architecture.md` is changed, followed by a re-review (rule-design-review: "Re-review architecture after approved modifications").

| Finding | Required change to architecture |
|---|---|
| DR-01 | Add a login throttle design (decision needed) |
| DR-02 | Confirm or replace C-10; add FR-12 acceptance criterion in requirements |
| DR-03 | Reconcile approval status of every decision and OQ-A item |
| DR-04 | Define public-route CSRF handling and a single CSRF failure status |
| DR-05 | Replace the "session id regenerated" claim with an actual mechanism; per-request user re-check; technical session lifetime |
| DR-06 | Restrict the post-login redirect target |
| DR-07 | Make the `Secure` cookie flag a required setting; define forwarded-header trust |
| DR-08 | Add busy-timeout handling; map only the email-index violation to the email error; mandatory real-connection race test |
| DR-09 | Require parameter hiding and log scrubbing; extend security tests |
| DR-10 | Technical password floor; dummy hash check; prefer prompt over environment variable |
| DR-11 | Add schema initialisation/versioning and session lifecycle |
| DR-12 | Add deployment requirements for the database file |
| DR-13 | Define technical per-field and body ceilings (values by human) |
| DR-14 to DR-16, DR-18, DR-21, DR-22 | Editorial and small design corrections as described in each finding |

Findings that do not require architecture changes: DR-19 (wording and practice), DR-20 (test plan additions inside the existing testing section), DR-17 (accept or add idempotency), DR-23, DR-24.

## 10. Unresolved Questions

Carried from requirements (all `Not Found`): OQ-2 department names, OQ-10 future-date range, OQ-11 field limits, OQ-12 normal operating conditions, OQ-15 password, lockout, timeout and logout rules, OQ-16 other roles, OQ-17 user-management capabilities, OQ-18 audit retention/format/viewing, email maximum length, retention and PII rules, E-6, E-10, E-12 data preservation, E-13, E-14, E-15, N-10 display style, message wording.

Raised by the architecture and still open: OQ-A1 (CLI vs web user management), OQ-A2 (atomic audit blocks creation), OQ-A3 (deployment and HTTPS termination), OQ-A4 (no encryption at rest for personal data), OQ-A5 (username in failed-login log).

Raised by this review:
- RQ-1: Which brute-force control is acceptable (DR-01)? Answer: `Not Found`.
- RQ-2: Is there a technical minimum password rule (DR-10)? Answer: `Not Found`.
- RQ-3: Technical size ceilings (DR-13)? Answer: `Not Found`.
- RQ-4: Is the `POST /logout` route wanted (DR-16)? Answer: `Not Found`.
- RQ-5: Is the repeated-submit message acceptable (DR-17)? Answer: `Not Found`.
- RQ-6: Which of D-1 to D-14 are approved (DR-03)? Answer: `Not Found`.

## 11. Overall Verdict

Review 1 verdict (historical, Revision 1). The CURRENT verdict after re-review is in section 17.

Verdict: APPROVED_WITH_CONDITIONS

Rationale: No Critical finding. The architecture covers all approved FR, NFR and AC ids except FR-12, which is only minimally interpreted, and its core structure (modular Flask monolith, pure validation, database-enforced uniqueness, transactional audit) is sound. Two High findings (DR-01, DR-02) and eleven Medium findings must be resolved or explicitly accepted by a human, and the corresponding architecture amendments approved and re-reviewed, before implementation starts.

Conditions:
1. Human decisions on DR-01, DR-02, DR-03, DR-10, DR-12 and DR-13.
2. Approved amendments for DR-03 to DR-13 recorded in `docs/architecture.md` by its owner, then re-reviewed.
3. Requirements update with at least one acceptance criterion for FR-12 (requirements owner).

## 12. Approval Status

(Review 1 status. Current status: section 18.)

- Review status: COMPLETE, verdict recorded above.
- Architecture approval: not granted by this review. Approval requires a human decision after the conditions above are addressed.
- Pipeline state: not updated by this reviewer.
- Human sign-off: Not Found

---

# Re-review (Review 2): architecture Revision 2

## 13. Re-review Overview

| Item | Value |
|---|---|
| Inputs | `docs/architecture.md` Revision 2 (status in its section 13: Revision 2 PENDING re-review, not approved; original D-1 to D-14 recorded as approved 2026-11-20 as relayed by the coordinator) and `docs/requirements.md` (revised 2026-11-20: FR-12 revised, FR-14 to FR-17, AC-11 to AC-15, N-12 to N-19, E-16, E-17) |
| Method | Document-only. Each DR finding re-checked against the revised text; the revision was then reviewed for new defects. No library behaviour, code or test result is claimed as verified. Where a point depends on library or database behaviour it is labelled "to verify at implementation". |
| Evidence limits | The user delegation behind the "Default" values and the user answers to OQ-A1 to OQ-A7 are recorded only as statements inside the two documents (and the coordinator's request). The reviewer cannot confirm them independently. Human sign-off record beyond those statements: `Not Found`. |
| Counting rule | A residual issue of a "Partially resolved" DR finding that is tracked as an NR finding is counted once, under the NR id. |

## 14. Status of Prior Findings (DR-01 to DR-24)

| Id | Original severity | Status | Evidence in Revision 2 | Residual |
|---|---|---|---|---|
| DR-01 Brute force | High | Partially resolved | Lockout designed: D-15, 3.2, 8.1 (counter and `locked_until` on User, 5 failures, 15 minutes, FR-16, AC-14); test list 9.2 AC-14 | Spec gaps and availability risk: NR-03, NR-04 |
| DR-02 FR-12 user management | High | Resolved | Requirements FR-12, AC-11, AC-12 and traceability row; architecture C-10 (`init-db`, `create-user`, `deactivate-user`), D-11, section 2 rows FR-12, AC-11, AC-12; OQ-A1 recorded as answered | None. Bootstrap problem found separately (NR-01) |
| DR-03 Approval contradiction | Medium | Resolved | Architecture status block (header), section 10 per-decision Status column, section 12.2 answered vs new items, section 13 | Approval evidence is relayed, not independently verifiable (NR-09) |
| DR-04 Auth/CSRF ordering | Medium | Resolved | D-5, 8.3, C-3 public routes (`GET/POST /login`), section 7 rows (CSRF on login 403, unauthenticated logout 401, single 403 for CSRF), 6.2 step 3, 9.2 tests; CSRF-enabled-in-tests assertion in 9.2 | Minor behavioural details: NR-05 |
| DR-05 Session handling | Medium | Partially resolved | D-16, 8.1: unsupported "session id regenerated" claim removed; `auth_version` revocation; per-request reload of `is_active`/`role`; technical 8 h lifetime in C-7 table; flash carries only a key | Lifetime enforcement not in the per-request list, remember-me not addressed: NR-06 |
| DR-06 Open redirect | Medium | Resolved | D-17, C-2, 8.6, 6.3 step 2: `next` ignored; test in 9.2 | None |
| DR-07 Secure cookie behind proxy | Medium | Resolved | 8.1 (`SESSION_COOKIE_SECURE` fixed setting, default on; trusted proxy count default 0 not used for security decisions), C-7 required settings, 9.4 cookie flag test | None |
| DR-08 Race / lock behaviour | Medium | Resolved | D-20, 7.3, C-5 (rollback, re-query `email_normalized`, else generic failure), C-7 busy wait 2 s, mandatory two-connection race test and non-email integrity test in 9.2 | Transaction scope detail: NR-07 (Low) |
| DR-09 PII in logs | Medium | Resolved | D-21, C-6 engine setting hiding parameters, 8.7, 9.4 log-capture test with known email and fallback filter | Library behaviour must be verified at implementation (architecture says so in 12.3) |
| DR-10 Password handling | Medium | Resolved | FR-16 (12 characters, not empty), FR-12 (no environment passwords), C-4 password rule, C-10 prompt only, 8.4 dummy hash, 9.3 tests including environment variable ignored | The "response time does not reveal usernames" claim is overstated: NR-02 |
| DR-11 Schema and session lifecycle | Medium | Partially resolved | D-19, C-6 session lifecycle, `init-db`, startup schema verification | The mechanism as written conflicts with `init-db` bootstrap: NR-01 |
| DR-12 NFR-2 enforcement | Medium | Partially resolved | New 8.8: database location setting outside served directory and repository, excluded from version control, service-account-only access, POSIX warning, backups carry restrictions | The architecture cannot enforce this; non-POSIX platforms rely on the operator; deployment target `Not Found` (OQ-A3). Residual Low, counted under DR-12 |
| DR-13 Field limits | Medium | Resolved | FR-15 defaults; D-9, 6.1 column sizes, 6.5 rules, C-3 413, 9.1 and 9.2 boundary tests | Defaults are not stakeholder-specified (see NR-09) |
| DR-14 Dangling ids | Low | Resolved | Section 2 now cites AS-5, AS-6; E-10 and E-13 listed as unmapped | New minor traceability gaps: NR-11 |
| DR-15 Diagram/text | Low | Resolved | Diagram edges checked against component dependency text: C-1, C-2, C-3, C-5, C-10 edges match; title corrected; C-4 receives today and limits from C-5 | None |
| DR-16 Logout, `is_active`, username | Low | Resolved | FR-14, FR-12 give both a requirement; username_normalized unique (6.1, D-18) | None |
| DR-17 Double submit | Low | Resolved | FR-17 and N-19 accept duplicate-email error; 7.2 states the consequence; C-9 static script compatible with CSP | None |
| DR-18 Unicode/normalisation | Low | Resolved | `casefold()` (D-3), trim definition (6.5, AS-6), non-ASCII digit and case-pair tests (9.1) | Observation only: `casefold` can treat some distinct non-ASCII addresses as equal; accepted by AS-8 |
| DR-19 Technology wording | Low | Resolved | Section 4 wording corrected, noise rows removed, pinning practice stated, vulnerability scanning `Not Found` | None |
| DR-20 Test gaps | Low | Resolved | 9.2 to 9.4 now include CSRF-enabled check, department tampering, 413, inactive login, login CSRF, headers, mandatory race test | New test gaps: NR-08 |
| DR-21 Hardening | Low | Resolved | D-22, C-1 debug refusal, C-3 `no-store`, 8.6 HSTS | None |
| DR-22 Audit integrity | Low | Resolved | D-23, 6.1 unique `employee_id`, C-6 no audit update/delete, startup index check | None |
| DR-23 Strengths | Informational | Noted | Retained; strengths still present in Revision 2 | None |
| DR-24 Project rules describe a CLI | Informational | Open | Architecture 12.3 records that the user decided not to change `CLAUDE.md` in this step | Human decision still pending |

Totals: Resolved 18 (DR-02, DR-03, DR-04, DR-06 to DR-10, DR-13 to DR-22), Partially resolved 4 (DR-01, DR-05, DR-11, DR-12), Open 1 (DR-24), Noted 1 (DR-23). Total 24.

## 15. New Findings Introduced by Revision 2

Severity scale unchanged. All are Open unless stated. IDs NR-01 onward are new and do not reuse any DR id.

#### NR-01 Startup checks conflict with the `init-db` and operator commands
- Category: Architecture Completeness / Component Design
- Severity: Medium
- Description: C-1 runs fail-fast startup checks on every application creation, including schema verification (tables and unique indexes must exist), a non-empty department list outside tests, and required settings. C-10 commands are Flask CLI commands, and `init-db` must run against a database that has no schema yet. As written the check would stop `init-db` before it can create the schema. The department-list check (D-10) would also block `create-user` and `deactivate-user` while the department names are `Not Found` (OQ-2), although account commands do not use departments. 9.2 tests that startup fails without the index, but no test covers `init-db` on an empty database.
- Evidence: architecture C-1 startup checks, C-10 (`init-db: creates the schema, then runs the schema verification`), D-10, D-19, 9.2 "Schema check", 9.3.
- Impact: The designed bootstrap path cannot work as written; operators cannot create the first account until the department list is configured.
- Recommendation: Amend architecture to state which checks apply to which entry point: serving the web application runs all checks; `init-db` needs only settings for database location; `create-user` and `deactivate-user` need the schema check but not the department list. Add the corresponding tests.
- Status: Open. Architecture change required.

#### NR-02 "Constant-work" login claim is overstated
- Category: Security
- Severity: Medium
- Description: 8.4 says that, because a hash comparison always runs, response time does not reveal valid usernames. The login flow (3.2) additionally performs a database write and independent commit only when the user exists, is active and is not locked (L7); unknown, inactive and locked accounts take the no-write path (L8). The extra commit is measurable work, so response time can differ between existing active accounts and the other cases, including inactive accounts. Status code and body are identical (good), but the timing claim is not achieved by the hash step alone.
- Evidence: architecture 3.2 nodes L3, L6 to L8, 8.4 last bullet, D-18 ("removes timing leak"), AC-13, requirement FR-16.
- Impact: Possible username enumeration and discovery of deactivated accounts by timing, against the intent of AC-13.
- Recommendation: Either reword the claim to cover only the hash step and record the timing difference as an accepted risk, or specify equalised work on all failure paths (for example an equivalent write for non-counting cases). Do not add a test that asserts timing equality. This is a human decision on acceptance.
- Status: Open - Human decision (accept risk or equalise). Architecture change required either way (wording or flow).

#### NR-03 Lockout counter specification gaps
- Category: Security / Data Flow
- Severity: Medium
- Description: D-15 says the increment is atomic in a single statement and that the failure reaching the limit sets `locked_until`. The architecture does not say that the increment and the lock setting are one conditional statement, so two concurrent failures could be handled in separate steps. It also does not define (a) how a lock that has expired resets the count when the next failure arrives, (b) behaviour when the counter write itself fails because the database is busy (login answered generically, or 500; fail-open or fail-closed), (c) that concurrent in-flight attempts that passed the "not locked" check before the lock was set can exceed 5 guesses by up to the number of concurrent requests, and (d) interleaving of a success reset with failures on the same account. The 9.2 lockout tests are sequential only.
- Evidence: architecture 3.2 (L5, L7), 8.1 lockout bullet, C-6 ("committed in its own short transaction"), D-15, OQ-A12, 9.2 AC-14 test list.
- Impact: Lock can be weaker than FR-16 states under concurrency, or login can return a server error during counter write contention. These are plausible but not demonstrated; the actual database behaviour is to verify at implementation.
- Recommendation: Amend architecture to specify one conditional update that increments, handles expired locks and sets `locked_until` together; define a fail-closed behaviour with the same generic message and a log entry when the counter write fails; document the bounded overshoot as accepted; add a two-connection concurrent-failure test and an expired-lock reset test.
- Status: Open. Architecture change required.

#### NR-04 Lockout availability and operator recovery
- Category: Security / Maintainability
- Severity: Medium
- Description: The architecture accepts that anyone who knows a username can lock that account for 15 minutes repeatedly, with no per-source throttle (8.1 accepted risks, 12.3). There is only a single role and operator commands offer no unlock, reactivate or password reset (C-10, OQ-17 `Not Found`). Consequences: an attacker can keep all known administrator accounts locked indefinitely by repeated attempts; a forgotten password or accidental deactivation can only be handled by creating a new username (usernames stay unique including deactivated ones); the sole active administrator cannot be recovered without direct database edits. The accepted risk is documented, but the recovery gap is not mentioned.
- Evidence: architecture 8.1, 12.3 first risk bullet, C-10 ("Reactivate, password reset, delete: not designed"), 6.1 username unique, AS-10; requirements FR-12 ("Other account operations ... Not Found"), FR-16.
- Impact: Availability of the only way to add employees depends on an attacker not guessing usernames and on manual database intervention for recovery.
- Recommendation: Ask the human whether an operator command to clear a lock or reactivate an account is wanted (an addition to OQ-17), and whether a per-source throttle is acceptable. Record the decision either way.
- Status: Open - Human decision

#### NR-05 Detail gaps in 401/403 and CSRF-expiry behaviour
- Category: Error Handling
- Severity: Low
- Description: (a) 6.2 step 1 says "Wrong role or stale session: rejected" while section 7 gives 403 for wrong role and treats stale or inactive sessions as unauthenticated (401 or 302); the two should be stated once. (b) Unauthenticated `POST /logout` returns a 401 page for a user whose session has just expired, which is a dead end for that user. (c) CSRF tokens may have a library-default lifetime (to verify at implementation); a form or login page left open past it would return 403 and lose entered data; the architecture does not say how this is presented. (d) 401 is returned without stating an authentication challenge header; the requirement accepts 401 or 403.
- Evidence: architecture 6.2 step 1, section 7 rows on 403/401/logout, D-5, 8.3; requirements E-12 (data preservation `Not Found`), AC-08b.
- Impact: Confusing or inconsistent responses in edge cases; no security weakness identified.
- Recommendation: Align 6.2 with section 7; make 401/403 pages offer a link to login; state the CSRF token lifetime setting and its user-facing handling; optionally return 403 instead of 401 if the challenge header is unwanted (both are allowed by AC-08b).
- Status: Open

#### NR-06 Session lifetime enforcement and cookie details
- Category: Security
- Severity: Low
- Description: The technical 8-hour lifetime is set in C-7 and the issue time is stored at login (6.3), but the per-request rejection list in C-2 (missing, inactive, wrong role, stale `auth_version`) does not include an issue-time check. The Flask-Login "remember me" cookie is not addressed (whether it is disabled). Logout ending every session of the user is flagged as OQ-A10 and awaits approval. Increment of `auth_version` is not stated to be a single atomic update.
- Evidence: architecture C-2 behaviour list, C-7 table, 6.3 step 2, 8.1, OQ-A8, OQ-A10.
- Impact: Lifetime might be enforced only by the browser cookie or signature age instead of the stored issue time; extra persistent login cookie could weaken logout and lifetime expectations.
- Recommendation: Add the issue-time check to C-2, state that remember-me is not used, state that `auth_version` changes are atomic increments, and add tests for lifetime expiry and for logout with an already-stale session.
- Status: Open. Architecture change required (small).

#### NR-07 SQLite transaction scope of the duplicate pre-check
- Category: Error Handling / Data Flow
- Severity: Low
- Description: The architecture does not say whether the duplicate-email pre-check runs inside the same transaction as the later insert. In SQLite a transaction that starts with a read and later tries to write while another connection has written can fail immediately as a locked error without waiting for the busy wait (to verify at implementation). That would surface in E-8 and E-9 as the generic 500 instead of "email already in use", more often than 7.3 suggests. Whether write-ahead logging is used is not stated; `deactivate-user` and `create-user` also write from a separate process.
- Evidence: architecture 7.3 ("its likelihood ... is unknown"), C-5, C-6 engine settings, D-20, 9.2 mandatory race test.
- Impact: Wrong user-visible message in concurrent submissions; no data integrity loss, because the unique index still holds.
- Recommendation: State that the pre-check runs outside the write transaction or that the write transaction begins as a write transaction; decide on journal mode; let the mandatory race test (9.2) assert the observed outcome.
- Status: Open

#### NR-08 Test plan gaps after the revision
- Category: Testability
- Severity: Low
- Description: Missing from section 9: concurrent failed-login test (see NR-03), `init-db` on an empty database through the same startup path as the CLI (NR-01), session lifetime expiry and stale-session logout (NR-06), the locked-account case in the "identical status and body" test (9.2 AC-13 lists unknown, wrong password and inactive only, but section 7 says locked is identical too), a check that the dummy-hash path runs for unknown users (functional, not timing), `Cache-Control` on the login page and 401/403/413 pages.
- Evidence: architecture 9.2 AC-13, AC-14, AC-15, 9.3; section 7 login rows.
- Impact: Designed behaviour could ship untested, contrary to the project rule that every behaviour gets a test.
- Recommendation: Add these cases to section 9.
- Status: Open

#### NR-09 Governance of delegated defaults and approval trail
- Category: Requirements Traceability / Governance
- Severity: Low
- Description: The requirements were materially extended after approval (FR-14 to FR-17, FR-12 reinterpreted, AC-11 to AC-15), but their approval block states "Approval status unchanged" with the original date, and every added value is labelled a default adopted by user delegation, not a stakeholder-specified value. Several are security relevant (lockout numbers, minimum password length, session behaviour). Architecture section 13 records original approval "as relayed in the coordinator's revision request" and "Human sign-off record beyond that message: `Not Found`".
- Evidence: requirements change log, FR-12 to FR-17, section 12; architecture 13.
- Impact: Risk that the approver did not see the final values or that the approval is treated as covering more than it does.
- Recommendation: Request an explicit human confirmation of the revised requirements and of the delegated defaults (a record of that confirmation is `Not Found` in the reviewed documents).
- Status: Open - Human decision

#### NR-10 Observability limits of the logging rules
- Category: Security
- Severity: Informational
- Description: Logs exclude attempted usernames (user decision, OQ-A5) and no source address is used (proxy count 0, no per-source control). Failed logins are all answered with 200 and the login form (OQ-A13), so status-based monitoring cannot spot attacks. Detection relies on the reason category and lockout events keyed by user id.
- Evidence: architecture C-11, 8.7, 8.1, OQ-A5, OQ-A13.
- Impact: Brute-force attempts against unknown usernames leave little trace. Accepted by user decision; no change proposed.
- Recommendation: Keep as a documented trade-off; revisit if NR-04 leads to a per-source throttle.
- Status: Noted

#### NR-11 Minor traceability gaps for new ids
- Category: Requirements Traceability
- Severity: Low
- Description: Architecture section 2 maps FR-12 to FR-17 and AC-11 to AC-15, but does not individually map E-16, E-17, N-17, or P-10 to P-13; the FR-14 row omits C-9 (logout control and form); E-16 (locked attempts for nonexistent usernames) is answered by the architecture (not counted, generic message) while the requirement says that behaviour is `Not Found`, a Proposal that appears only as OQ-A12. All other new ids (FR-14 to FR-17, AC-11 to AC-15, N-12 to N-16, N-18, N-19) have a component and a test.
- Evidence: architecture section 2 rows FR-14, FR-16, N-12 to N-19, OQ-A12; requirements E-16, E-17, N-17, P-10 to P-13.
- Impact: Small risk that a requirement scenario is left without a named test.
- Recommendation: Add the missing ids to section 2 rows and section 9.
- Status: Open

### 15.1 Review of the new proposals

| Item | Assessment |
|---|---|
| D-15 lockout in database | Sound choice (survives restart, multiple workers). Specification gaps NR-03; recovery and availability NR-04 |
| D-16 `auth_version` | Closes the revocation gap in DR-05; details NR-06; logout ends all sessions (OQ-A10) |
| D-17 fixed redirect | Adequate; no issue |
| D-18 password and login behaviour | Meets FR-16 and FR-12; timing claim NR-02; 200-on-failure acceptable and identical for all causes (OQ-A13), monitoring effect NR-10 |
| D-19 schema and sessions | Sound idea; bootstrap conflict NR-01 |
| D-20 re-query on integrity error | Correct approach, avoids parsing database text; scope detail NR-07 |
| D-21 hide parameters, deployment constraints | Adequate at design level; verify at implementation |
| D-22 hardening | Adequate |
| D-23 audit integrity | Adequate; employee/audit consistency still holds (one transaction, unique `employee_id`, startup index check) |
| OQ-A8 to OQ-A14 | All are Proposals awaiting a human answer; none was found to be unreasonable. OQ-A14 (prompt only, not scriptable) is consistent with FR-12 |

## 16. Re-review Findings Summary

Counts of open items after re-review (resolved items excluded; Noted items excluded):

| Severity | Count | IDs |
|---|---|---|
| Critical | 0 | none |
| High | 0 | none |
| Medium | 4 | NR-01, NR-02, NR-03, NR-04 |
| Low | 7 | DR-12 (residual), NR-05, NR-06, NR-07, NR-08, NR-09, NR-11 |
| Informational | 2 | DR-24, NR-10 |
| Total open | 13 | |

New findings in this re-review: 11 (NR-01 to NR-11): Medium 4, Low 6, Informational 1.
Prior findings DR-01 to DR-24: Resolved 18, Partially resolved 4 (DR-01, DR-05, DR-11 tracked by NR items; DR-12 counted above), Open 1 (DR-24), Noted 1 (DR-23).

Highs from Review 1 (DR-01, DR-02): DR-02 resolved; DR-01 reduced to Medium residual (NR-03, NR-04).

## 17. Overall Verdict (Review 2, superseded by section 23)

Verdict: APPROVED_WITH_CONDITIONS

Rationale: All Review 1 High findings are addressed or reduced to Medium. Revision 2 fixes the substantive problems from Review 1 (session mechanism, CSRF ordering, open redirect, secure cookie, PII in logs, schema lifecycle, limits). No Critical or High finding remains. One new defect (NR-01) would block the operator bootstrap path as written, and the lockout and timing specifications (NR-02, NR-03) are not yet precise enough to implement without guessing, so conditions remain.

Conditions:
1. Architecture owner amends NR-01, NR-02 (wording or flow), NR-03 and NR-06, and tidies NR-05, NR-07, NR-08 and NR-11; changes are then re-checked (rule: re-review after approved modifications).
2. Human decisions listed in section 18.
3. Revision 2 itself (D-15 to D-23 and the amendments to D-3, D-5, D-9, D-11) remains not approved until a human approves it. This review does not approve the architecture.

## 18. Human Decisions Needed and Approval Status (Review 2, superseded by section 24)

Human decision required:
- NR-04: whether an operator unlock or reactivate command is wanted, and whether the known-username lockout risk (and no per-source throttle) is accepted.
- NR-02: accept the timing difference or require equalised work.
- NR-09: confirm the revised requirements and the delegated defaults (FR-12 to FR-17); approval trail beyond the coordinator's message is `Not Found`.
- OQ-A8 to OQ-A14: approve or change the seven new Proposals (8-hour technical session lifetime, 2-second busy wait, logout ends all sessions, case-insensitive usernames capped at 100 characters, lock and counting semantics, 200 on every login failure, prompt-only account commands).
- DR-12 and OQ-A3: deployment target and platform (`Not Found`); NFR-2 file protection is operator-owned.
- DR-24: whether to update `CLAUDE.md` and the package layout (not an architecture change).

Architecture changes required (not applied; need human approval): NR-01, NR-02 (either option), NR-03, NR-06, NR-07. Editorial or test-plan only: NR-05, NR-08, NR-11.

Approval status:
- Review status: COMPLETE (re-review of Revision 2).
- Architecture approval: not granted by this review.
- Pipeline state: not updated by this reviewer.
- Human sign-off: Not Found

---

# Final re-check (Review 3): architecture Revision 3

## 19. Review 3 Overview

| Item | Value |
|---|---|
| Inputs | `docs/architecture.md` Revision 3 (revision log section 14: fixes for NR-01 to NR-11, `unlock-user`, D-24, D-25, OQ-A15) and `docs/requirements.md` with FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18, OQ-19 (user-approved addition, 2026-11-20) |
| Method | Document-only. Each NR finding and the residual DR findings re-checked against the text; Revision 3 then checked for new defects (lockout statement, startup-check table, `unlock-user`, D-25, traceability). No library, database or test behaviour is claimed as verified; such points are labelled "to verify at implementation". |
| Evidence limits | User approvals are recorded only as statements in the documents (relayed through the coordinator). Written sign-off record: `Not Found`. |

## 20. Status of Earlier Findings

Status values: Resolved, Partially resolved, Open.

| Id | Prior status | Review 3 status | Evidence in Revision 3 | Remaining point |
|---|---|---|---|---|
| NR-01 Startup checks vs `init-db` | Open | Resolved | C-1 table of checks per entry point (web app, `init-db`, user commands); C-10 "command context ... only the database settings group"; C-7 "Required for operator commands: database location only"; D-24; 9.2 "Entry-point checks (D-24)" tests `init-db` on an empty database without signing key or department list | None |
| NR-02 Timing claim | Open - Human decision | Resolved | 8.4 now states the timing difference as a known limitation accepted by the user; no timing-safe claim; no equalised work; D-18 and 12.3 repeat it; 13 records the acceptance | Accepted risk, not a defect |
| NR-03 Lockout specification | Open | Resolved | 6.3 steps 2 to 4: one conditional update that counts, resets an expired lock and sets the lock at 5 in the same statement; conditional success reset; fail closed with the generic message; overshoot bounded and accepted; 3.2 diagram agrees; 9.2 mandatory concurrency test and fail-closed tests | New detail on lockout write while locked: NR-12 |
| NR-04 Lockout availability and recovery | Open - Human decision | Resolved | `unlock-user` (C-10, D-15, 6.4); accepted risks recorded in 8.1 and 12.3 as user-approved; requirements FR-18, AC-16, AC-17 added | Reactivation, password reset and forgotten-password procedure remain `Not Found` (OQ-19); this is an open question, not a defect. Per-source throttle not designed (accepted) |
| NR-05 401/403, CSRF expiry | Open | Resolved | 6.2 steps 1 and 3 match section 7 and 3.1; C-3 error pages with login link; C-7 and 8.3 CSRF token lifetime equals the session lifetime; C-2 states no `WWW-Authenticate` header | OQ-A15 (keep 401 or use 403) awaits a human answer |
| NR-06 Session lifetime and cookie | Open | Resolved | C-2 per-request check includes issue time against the C-8 clock; "remember me" not used (section 4, C-2, D-16); atomic `auth_version` increment; stale logout gives 401 with no increment; 9.2 tests lifetime expiry, stale logout, no remember-me cookie | None |
| NR-07 SQLite transaction scope | Open | Resolved | D-25, C-5, C-6, 3.1 sequence (pre-check ended before the write transaction), 7.3, 9.2 race test | Operational details of the D-25 proposal: NR-14 |
| NR-08 Test plan gaps | Open | Resolved | 9.2 now covers concurrency, fail-closed, locked case in the identical-response test, dummy-hash functional test, lifetime, stale logout, entry-point checks, headers on login and error pages (9.4) | `unlock-user` tests incomplete: NR-13 |
| NR-09 Approval trail for defaults | Open - Human decision | Partially resolved | Architecture section 13 records the approval trail ("Fix and continue" 2026-11-20) and "written sign-off records: `Not Found`"; requirements revision log (line 7) records the user-approved unlock addition | Requirements section 12 approval text (Revision paragraph) mentions the delegated defaults but not FR-18; approval is relayed, not independently verifiable. Residual Low, human confirmation |
| NR-10 Observability | Noted | Resolved (recorded) | Trade-off recorded in 8.7 and 12.3 | None |
| NR-11 Traceability of new ids | Open | Resolved | Section 2 maps FR-14 to C-9, E-16, E-17, N-10, N-17, P-1 to P-13, N-12 to N-19 | The new ids FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18, OQ-19 are not mapped: NR-13 |
| DR-01 Brute force | Partially resolved | Resolved | NR-03 and NR-04 resolved as above; lockout designed (D-15, 6.3) with accepted availability risk | None beyond NR-12 |
| DR-05 Session handling | Partially resolved | Resolved | NR-06 resolved | None |
| DR-11 Schema and session lifecycle | Partially resolved | Resolved | NR-01 resolved; D-19 scoped by D-24 | None |
| DR-12 NFR-2 enforcement | Partially resolved | Resolved at design level | 8.8 states the limit explicitly ("the application cannot enforce file permissions ... residual risk, not closed by the design"), covers journal files, operator accounts, POSIX warning; 12.3 repeats | The deployment target stays `Not Found` (OQ-A3); an open question, not a defect. WAL-related file handling: NR-14 |
| DR-24 Project rules describe a CLI | Open | Open | Architecture 12.2 and 12.3: "left for implementation planning; not changed" | Human decision still pending (Informational) |

## 21. New Findings in Revision 3

#### NR-12 Lockout update is attempted while the account is already locked
- Category: Data Flow / Error Handling
- Severity: Low
- Description: In Revision 2 the failure path skipped the counter write for a locked account. In Revision 3 the flow in 3.2 sends every failed login for an existing active account to the conditional update (node L7), including while the account is locked, where the update is specified to change nothing (6.3 step 2). The statement is a safe no-op for the counter, but it is still a database write attempt on every login failure for a known username. A write attempt on SQLite may take the single writer lock even when no row changes (to verify at implementation). Anyone who knows a username can therefore generate write contention that competes with employee creation, which is subject to the 2-second busy wait and the generic 500. Each attempt also costs a password hash, and no per-source throttle exists (accepted in 8.1).
- Evidence: architecture 3.2 (L4 to L7: the locked branch is not separated), 6.3 steps 2 and 3, C-6 (lockout updates commit in their own transaction), C-7 (busy wait), 8.1 accepted risks, 9.2 lockout tests (no test for the write-while-locked case).
- Impact: Availability of the main function can be degraded by repeated login failures against a locked known account. Not demonstrated; depends on database behaviour.
- Recommendation: Keep the conditional statement as the safety net, but skip the write when the earlier read already shows the account locked, and add a test that no write is issued for a locked account. Alternatively record the contention as an accepted risk with the others in 8.1.
- Status: Open (small architecture change, or an accepted-risk note)

#### NR-13 Traceability and tests for FR-18, AC-16, AC-17, N-20 and E-18 are missing from the architecture
- Category: Requirements Traceability / Testability
- Severity: Low
- Description: Requirements now contain FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18 and OQ-19. The architecture still says the requirements update for `unlock-user` is pending (1.4, C-10 heading text, 12.2, 13) and section 2 has no rows for these ids; the FR-12 row refers to "requirements update pending". Specifics:
  - E-18 (unlock for a username that does not exist) is `Not Found` in requirements, while the architecture states "a clear error and non-zero exit" (C-10, 9.3) without marking it as a Proposal or open item.
  - 9.3 tests unlock after lockout, idempotency, `is_active` unchanged and the unknown-username error. It does not state tests that the password is unchanged (AC-17), that a deactivated account stays unable to log in after unlock (N-20), or that the lock and count are cleared in one update (concurrent failure racing an unlock).
  - OQ-19 is not cited; reactivation, password reset and the forgotten-password procedure appear under OQ-17.
- Evidence: architecture 1.4, 2 (FR-12 row), C-10, 9.3, 12.1, 12.2, 13; requirements FR-12, FR-18, AC-16, AC-17, N-20, E-18, OQ-19, traceability table row "User-approved addition, unlock-user".
- Impact: A requirement scenario could be left without a named test; the architecture states an outdated "pending" position.
- Recommendation: Map FR-18 to C-10, C-6 and C-8; AC-16, AC-17, P-14, P-15, N-20 and E-18 to the 9.3 tests; add the missing test cases; mark the unknown-username behaviour as a Proposal pending confirmation of E-18; replace the "pending" statements; cite OQ-19.
- Status: Open

#### NR-14 D-25 operational details: journal mode and the race-test pass criterion
- Category: Technology Selection / Error Handling
- Severity: Low
- Description: D-25 adds the write-ahead journal mode as a Proposal. The architecture does not say how it behaves if the database sits on a network file system, nor how journal and shared-memory files are created and owned when the web service and the operator commands run as different accounts, although 8.8 requires both accounts to have access. Deployment target is `Not Found` (OQ-A3). Separately, the mandatory race test "asserts and records" whether the loser sees the email-in-use error or the generic failure (9.2), so it can pass in either case and so does not enforce the D-25 intent that the duplicate message appears reliably. The pre-check-then-write ordering in D-25 does not itself depend on the journal mode.
- Evidence: architecture C-6 engine settings, D-25, 7.3, 8.8, 9.2 race test, OQ-A3.
- Impact: Possible deployment surprises; weaker test gate. No effect on data integrity (the unique index holds).
- Recommendation: State that the journal mode is chosen after the deployment target is known and that the write-begin ordering stands without it; make the race test assert the expected outcome and treat the other outcome as a defect to investigate.
- Status: Open

#### NR-15 Operator actions are only in application logs
- Category: Security
- Severity: Informational
- Description: `create-user`, `deactivate-user` and `unlock-user` log the command name and user id (C-11), but nothing durable records which operator ran them or in what order. This matters more for `unlock-user`, which removes a security control. The requirements demand an audit only for employee creation (FR-13); no requirement asks for more.
- Evidence: architecture C-11, C-10; requirements FR-13, OQ-18 `Not Found`.
- Impact: Limited accountability for account administration. Not required by any approved requirement.
- Recommendation: No change required. Note it as a possible future requirement together with OQ-18.
- Status: Noted

### 21.1 Checks requested for Revision 3

| Check | Result |
|---|---|
| Atomic lockout statement | Design is sound and precise (6.3): one conditional update counts, resets an expired lock and sets the lock; success reset is conditional; fail closed; overshoot bounded and accepted. Only the write-while-locked detail remains (NR-12) |
| Startup-check table per command | Consistent across C-1, C-7, C-10, D-10, D-24 and 9.2 tests. Commands do not call the web factory; no conflict found with the diagram (C-10 depends on C-4, C-6, C-7, C-8) |
| `unlock-user` | Matches FR-18 (clears count and lock, idempotent, no change to `is_active` or password). Does not alter `auth_version`, which is correct. Gaps are in traceability and tests (NR-13) and accountability (NR-15) |
| D-25 transaction scope | Sound in principle (pre-check ended before a write that begins as a write); operational points NR-14; behaviour of the library and database remains to verify at implementation (the architecture says so) |
| Traceability for FR-18, AC-16, AC-17, N-20 | Not yet reflected in the architecture (NR-13). Requirements side is complete: FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18, OQ-19 and the traceability row exist |
| Consistency of 401/403/302, login and logout ordering | 3.1, 6.2, 6.3, 7 and 8.3 agree. No new inconsistency found |

## 22. Findings Summary after Review 3

Open items (resolved items excluded; Noted items excluded):

| Severity | Count | IDs |
|---|---|---|
| Critical | 0 | none |
| High | 0 | none |
| Medium | 0 | none |
| Low | 4 | NR-09 (partially resolved), NR-12, NR-13, NR-14 |
| Informational | 1 | DR-24 (open) |
| Total open | 5 | |

New in Review 3: 4 findings (NR-12, NR-13, NR-14 Low; NR-15 Informational, Noted).
Status of the earlier items checked in this review (16): Resolved 14, Partially resolved 1 (NR-09), Open 1 (DR-24). Of the original 24 DR findings and 11 NR findings, none is Critical, High or Medium any longer.

## 23. Overall Verdict (CURRENT)

Verdict: APPROVED_WITH_CONDITIONS

Rationale: Every Medium and High finding raised in Reviews 1 and 2 is resolved or turned into an explicit, user-approved accepted risk (known-username lockout, timing difference, no per-source throttle, overshoot). Revision 3 introduces no Medium or higher defect. Four Low findings and one Informational item remain. The conditions are small, and none requires redesign:
1. Architecture owner updates the architecture for NR-13 (traceability and tests for FR-18, AC-16, AC-17, N-20, E-18, OQ-19, stale "pending" statements), and considers NR-12 and NR-14.
2. Human decisions in section 24.
3. Revision 3 items (D-24, D-25, OQ-A15, CSRF token lifetime, the Rev 3 refinements to D-5, D-10, D-11, D-15, D-16, D-18, D-19) are recorded as "approved pending re-check" and "not otherwise approved" in the architecture itself; this review does not approve them. Approval remains a human act.

## 24. Human Decisions, Unresolved Questions and Approval Status

Human decision needed:
- Approve or change the Revision 3 items: D-24, D-25 (including write-ahead journal mode, NR-14), CSRF token lifetime equal to the session lifetime, and the Rev 3 refinements to approved decisions.
- OQ-A15: keep 401 without a `WWW-Authenticate` header, or use 403 for unauthenticated submissions (AC-08b allows both).
- NR-09: confirm that the user approval covers the delegated defaults and the FR-18 addition as recorded in the requirements approval section; a written sign-off record is `Not Found`.
- E-18 / NR-13: confirm the unknown-username behaviour for `unlock-user` (requirement says `Not Found`; architecture proposes a clear error and non-zero exit).
- NR-12: accept the write attempt on locked accounts as a risk, or require the skip.
- DR-24: whether to update `CLAUDE.md` and the package layout (not an architecture change).

Unresolved questions (all `Not Found` in the documents): OQ-2 department names; OQ-11 residual (allowed characters, job title free text or list); OQ-12 normal operating conditions; OQ-15 residual (session timeout as a business rule, other password rules); OQ-16 other roles; OQ-17 and OQ-19 (reactivation, password reset, forgotten-password procedure); OQ-18 audit retention, format and viewing; OQ-A3 deployment target and platform; backup policy; written sign-off records; E-10, E-12 data preservation, E-13, E-15 beyond FR-17, N-10 display style, wording of validation and server error messages.

Architecture changes required: none that are blocking. Recommended amendments by the architecture owner (not applied by this review): NR-13, NR-12, NR-14.

Approval status:
- Review status: COMPLETE (Review 3).
- Architecture approval: not granted by this review.
- Pipeline state: not updated by this reviewer.
- Human sign-off: Not Found
