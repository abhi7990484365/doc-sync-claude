"""TASK-027: login route (FR-12, FR-16, AC-11, AC-13, N-12, N-13, P-10)."""

import logging

import pytest

from employee_app.db.users import deactivate_user_by_id
from employee_app.security import dummy_hash
from tests.conftest import add_user, login_secret_for_tests
from tests.web_helpers import login, strip_tokens

SECRET = login_secret_for_tests()
WRONG = "definitely-not-the-login-value"


def test_account_created_through_the_command_path_logs_in_and_opens_the_form(client, admin_id) -> None:  # P-10
    response = login(client, "admin1", SECRET)
    assert response.status_code == 303
    assert response.headers["Location"].endswith("/employees/new")
    assert client.get("/employees/new").status_code == 200


def test_username_is_case_insensitive_and_trimmed(client, admin_id) -> None:
    assert login(client, "  ADMIN1 ", SECRET).status_code == 303


def test_unknown_user_wrong_secret_and_inactive_are_identical(client, engine) -> None:  # N-12, N-13
    add_user(engine, "admin1")
    inactive = add_user(engine, "gone1")
    deactivate_user_by_id(engine, inactive)
    responses = [login(client, "nobody", SECRET), login(client, "admin1", WRONG), login(client, "gone1", SECRET),
                 login(client, "gone1", WRONG)]
    assert {r.status_code for r in responses} == {200}
    bodies = {strip_tokens(r.get_data(as_text=True)) for r in responses}
    assert len(bodies) == 1
    assert "Sign in failed" in bodies.pop()


def test_failure_does_not_reveal_which_part_was_wrong(client, admin_id) -> None:
    body = login(client, "admin1", WRONG).get_data(as_text=True).lower()
    assert "username" not in body.split("sign in failed")[1][:80]
    assert "admin1" not in body


def test_failed_login_creates_no_session(client, admin_id) -> None:
    login(client, "admin1", WRONG)
    assert client.get("/employees/new").status_code == 302


def test_dummy_hash_is_verified_for_an_unknown_user(client, monkeypatch) -> None:
    seen: list[str] = []
    monkeypatch.setattr("employee_app.auth.login.verify_password", lambda h, p: seen.append(h) or False)
    login(client, "nobody", SECRET)
    assert seen == [dummy_hash()]


def test_real_hash_is_verified_for_an_existing_user(client, admin_id, monkeypatch) -> None:
    seen: list[str] = []
    monkeypatch.setattr("employee_app.auth.login.verify_password", lambda h, p: seen.append(h) or False)
    login(client, "admin1", WRONG)
    assert len(seen) == 1 and seen[0] != dummy_hash()


@pytest.mark.parametrize("target", ["http://evil.example/", "/logout", "//evil.example"])
def test_next_parameter_is_ignored(client, admin_id, target: str) -> None:
    from tests.web_helpers import page_token

    token = page_token(client)
    response = client.post(f"/login?next={target}", data={"csrf_token": token, "username": "admin1",
                                                          "password": SECRET}, follow_redirects=False)
    assert response.headers["Location"].endswith("/employees/new")


def test_empty_fields_fail_generically(client, admin_id) -> None:
    response = login(client, "", "")
    assert response.status_code == 200 and "Sign in failed" in response.get_data(as_text=True)


def test_session_is_reissued_on_login(client, admin_id) -> None:
    from tests.web_helpers import page_token

    token = page_token(client)
    with client.session_transaction() as s:
        s["planted"] = "old-value"
    client.post("/login", data={"csrf_token": token, "username": "admin1", "password": SECRET})
    with client.session_transaction() as s:
        assert "planted" not in s and s["auth_version"] == 0


def test_no_username_or_secret_is_logged(client, admin_id, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="employee_app"):
        login(client, "admin1", WRONG)
        login(client, "somebody-unknown", WRONG)
        login(client, "admin1", SECRET)
    text = " ".join(r.getMessage() for r in caplog.records)
    assert "admin1" not in text and "somebody-unknown" not in text
    assert WRONG not in text and SECRET not in text
    assert "login_success user_id=" in text and "login_failure category=" in text
