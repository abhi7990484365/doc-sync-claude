"""TASK-037: authentication and CSRF integration (AC-08, AC-08b, NFR-1; N-7, N-8, N-15, E-12)."""

from employee_app.db.users import deactivate_user_by_id
from tests.web_helpers import employee_counts, page_token, post_employee, set_role, valid_form


def test_n7_unauthenticated_get_redirects_to_login(client) -> None:
    response = client.get("/employees/new")
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")


def test_n8_unauthenticated_post_with_and_without_token_is_401_and_counts_unchanged(client, engine) -> None:
    with_token = post_employee(client, valid_form(), page_token(client, "/login"))
    without_token = client.post("/employees/new", data=valid_form())
    assert (with_token.status_code, without_token.status_code) == (401, 401)
    assert employee_counts(engine) == (0, 0)


def test_wrong_role_is_403_on_page_and_submission(logged_in, engine, admin_id) -> None:
    token = page_token(logged_in, "/employees/new")
    set_role(engine, admin_id, "other_role")
    assert logged_in.get("/employees/new").status_code == 403
    assert post_employee(logged_in, valid_form(), token).status_code == 403
    assert employee_counts(engine) == (0, 0)


def test_authenticated_post_with_missing_token_is_403_and_no_record(logged_in, engine) -> None:
    assert logged_in.post("/employees/new", data=valid_form()).status_code == 403
    assert employee_counts(engine) == (0, 0)


def test_e12_expired_session_then_submit_is_401(logged_in, engine, fixed_clock) -> None:
    token = page_token(logged_in, "/employees/new")
    fixed_clock.advance(hours=8, seconds=1)
    assert post_employee(logged_in, valid_form(), token).status_code == 401
    assert employee_counts(engine) == (0, 0)


def test_n15_after_logout_a_direct_submission_is_rejected(logged_in, engine) -> None:
    token = page_token(logged_in, "/employees/new")
    assert logged_in.post("/logout", data={"csrf_token": token}).status_code == 303
    assert post_employee(logged_in, valid_form(), token).status_code in (401, 403)
    assert employee_counts(engine) == (0, 0)


def test_deactivated_users_open_session_cannot_submit(logged_in, engine, admin_id) -> None:
    token = page_token(logged_in, "/employees/new")
    deactivate_user_by_id(engine, admin_id)
    assert post_employee(logged_in, valid_form(), token).status_code == 401
    assert employee_counts(engine) == (0, 0)


def test_token_from_an_open_form_stays_valid_within_the_session(logged_in, fixed_clock, engine) -> None:
    token = page_token(logged_in, "/employees/new")
    fixed_clock.advance(hours=7)  # CSRF lifetime equals the session lifetime
    assert post_employee(logged_in, valid_form(), token).status_code == 303
