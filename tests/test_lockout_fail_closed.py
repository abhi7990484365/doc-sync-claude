"""TASK-034: fail-closed lockout (NR-03, D-15). Three injection points."""

import logging

import pytest

from employee_app.db.errors import StorageError
from employee_app.db.users import find_user_by_username
from tests.conftest import login_secret_for_tests
from tests.web_helpers import login, strip_tokens

SECRET = login_secret_for_tests()
WRONG = "definitely-not-the-login-value"
USERNAME = "admin1"


def boom(*_a: object, **_k: object) -> bool:
    raise StorageError("OperationalError")


def baseline(client):  # type: ignore[no-untyped-def]
    response = login(client, "nobody-here", WRONG)
    return response.status_code, strip_tokens(response.get_data(as_text=True))


def assert_rejected_like_baseline(client, response, expected) -> None:  # type: ignore[no-untyped-def]
    assert (response.status_code, strip_tokens(response.get_data(as_text=True))) == expected
    assert client.get("/employees/new").status_code == 302  # no session was granted


def error_records(caplog):  # type: ignore[no-untyped-def]
    return [r for r in caplog.records if r.levelno >= logging.ERROR]


def test_counter_write_failure_on_the_failure_path(client, admin_id, monkeypatch, caplog) -> None:
    expected = baseline(client)
    monkeypatch.setattr("employee_app.auth.login.record_failure", boom)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        response = login(client, USERNAME, WRONG)
    assert_rejected_like_baseline(client, response, expected)
    errors = error_records(caplog)
    assert [r.getMessage() for r in errors] == [f"login_storage_error category=OperationalError user_id={admin_id}"]
    assert USERNAME not in caplog.text


def test_counter_write_failure_on_the_success_path_never_grants_a_session(client, admin_id, monkeypatch, caplog) -> None:
    expected = baseline(client)
    monkeypatch.setattr("employee_app.auth.login.record_success", boom)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        response = login(client, USERNAME, SECRET)  # correct value, but the reset write fails
    assert_rejected_like_baseline(client, response, expected)
    assert [r.getMessage() for r in error_records(caplog)] == [
        f"login_storage_error category=OperationalError user_id={admin_id}"]
    assert USERNAME not in caplog.text and SECRET not in caplog.text


def test_lock_state_read_failure(client, admin_id, monkeypatch, caplog) -> None:
    expected = baseline(client)
    monkeypatch.setattr("employee_app.auth.login.find_user_by_username", boom)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        response = login(client, USERNAME, SECRET)
    assert_rejected_like_baseline(client, response, expected)
    errors = error_records(caplog)
    # the account could not be read, so no user id is known: category only
    assert [r.getMessage() for r in errors] == ["login_storage_error category=OperationalError"]
    assert USERNAME not in caplog.text


def test_success_update_reporting_no_row_rejects_the_login(client, admin_id, monkeypatch) -> None:
    expected = baseline(client)
    monkeypatch.setattr("employee_app.auth.login.record_success", lambda *a, **k: False)
    assert_rejected_like_baseline(client, login(client, USERNAME, SECRET), expected)


@pytest.mark.parametrize("target", ["record_failure", "record_success"])
def test_failed_counter_write_leaves_the_stored_counter_unchanged(client, engine, admin_id, monkeypatch, target) -> None:
    monkeypatch.setattr(f"employee_app.auth.login.{target}", boom)
    login(client, USERNAME, WRONG if target == "record_failure" else SECRET)
    assert find_user_by_username(engine, USERNAME).failed_login_count == 0
