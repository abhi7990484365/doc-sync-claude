"""TASK-040: account and session scenarios AC-11 to AC-15 (P-10, P-11, N-12, N-13, N-14, N-15, N-16)."""

import secrets

from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.conftest import login_secret_for_tests
from tests.web_helpers import login, page_token, strip_tokens

SECRET = login_secret_for_tests()
WRONG = "definitely-not-the-login-value"


def test_ac11_p10_operator_created_account_logs_in_and_sees_the_form(app, db_file, engine) -> None:
    secret = secrets.token_urlsafe(18)
    assert run_cli(["create-user"], cmd_env(db_file), create_user_input("new.admin", secret)).exit_code == 0
    client = app.test_client()
    assert login(client, "new.admin", secret).status_code == 303
    assert client.get("/employees/new").status_code == 200


def test_ac12_n12_deactivated_account_is_rejected_at_login(app, db_file, admin_id) -> None:
    assert run_cli(["deactivate-user", "admin1"], cmd_env(db_file)).exit_code == 0
    client = app.test_client()
    response = login(client, "admin1", SECRET)
    assert response.status_code == 200 and client.get("/employees/new").status_code == 302


def test_ac12_open_session_of_a_deactivated_account_is_rejected_on_its_next_request(logged_in, db_file) -> None:
    assert logged_in.get("/employees/new").status_code == 200
    assert run_cli(["deactivate-user", "admin1"], cmd_env(db_file)).exit_code == 0
    assert logged_in.get("/employees/new").status_code == 302


def test_ac13_n13_one_generic_message_for_every_cause(app, engine, db_file, admin_id) -> None:
    from employee_app.db.users import deactivate_user_by_id
    from tests.conftest import add_user

    gone = add_user(engine, "gone1")
    deactivate_user_by_id(engine, gone)
    locked = add_user(engine, "locked1")
    client = app.test_client()
    for _ in range(5):
        login(client, "locked1", WRONG)
    responses = [login(client, "nobody", SECRET), login(client, "admin1", WRONG), login(client, "gone1", SECRET),
                 login(client, "locked1", SECRET)]
    assert locked
    assert {r.status_code for r in responses} == {200}
    assert len({strip_tokens(r.get_data(as_text=True)) for r in responses}) == 1


def test_ac14_n14_lockout_cycle_with_replaced_clock(app, admin_id, fixed_clock) -> None:
    client = app.test_client()
    for _ in range(5):
        login(client, "admin1", WRONG)
    assert login(client, "admin1", SECRET).status_code == 200
    fixed_clock.advance(minutes=15)
    assert login(client, "admin1", SECRET).status_code == 303


def test_ac15_p11_logout_ends_the_session(logged_in) -> None:
    token = page_token(logged_in, "/employees/new")
    assert logged_in.post("/logout", data={"csrf_token": token}).status_code == 303
    assert logged_in.get("/employees/new").status_code == 302


def test_ac15_n15_n16_logout_without_token_fails_and_get_does_nothing(logged_in) -> None:
    assert logged_in.post("/logout").status_code == 403
    assert logged_in.get("/logout").status_code == 405
    assert logged_in.get("/employees/new").status_code == 200


def test_session_lifetime_expiry(logged_in, fixed_clock) -> None:
    fixed_clock.advance(hours=8, seconds=1)
    assert logged_in.get("/employees/new").status_code == 302


def test_no_remember_me_cookie_is_issued(app, admin_id) -> None:
    client = app.test_client()
    response = login(client, "admin1", SECRET)
    assert all(not c.startswith("remember_token") for c in response.headers.getlist("Set-Cookie"))
