"""TASK-028: lockout in login incl. NR-12 and fail-closed (AC-14, N-14, E-16)."""

from datetime import timedelta

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.engine import Engine

from employee_app.db.engine import session_scope
from employee_app.db.models import User
from employee_app.db.users import find_user_by_username
from tests.conftest import login_secret_for_tests
from tests.web_helpers import build_app, login, strip_tokens

SECRET = login_secret_for_tests()
WRONG = "definitely-not-the-login-value"


def fail(client, times: int) -> None:  # type: ignore[no-untyped-def]
    for _ in range(times):
        login(client, "admin1", WRONG)


def user(engine):  # type: ignore[no-untyped-def]
    return find_user_by_username(engine, "admin1")


def test_fifth_failure_locks_and_correct_value_is_rejected_for_15_minutes(client, engine, admin_id, fixed_clock) -> None:
    fail(client, 4)
    assert user(engine).locked_until is None
    fail(client, 1)
    assert user(engine).locked_until == fixed_clock.now + timedelta(minutes=15)
    fixed_clock.advance(minutes=14, seconds=59)
    assert login(client, "admin1", SECRET).status_code == 200
    fixed_clock.advance(seconds=1)
    assert login(client, "admin1", SECRET).status_code == 303


def test_locked_response_is_identical_to_wrong_credentials(client, engine, admin_id) -> None:
    wrong = login(client, "admin1", WRONG)
    fail(client, 4)
    locked = login(client, "admin1", SECRET)
    assert locked.status_code == wrong.status_code == 200
    assert strip_tokens(locked.get_data(as_text=True)) == strip_tokens(wrong.get_data(as_text=True))


def test_expired_lock_restarts_count_at_one(client, engine, admin_id, fixed_clock) -> None:
    fail(client, 5)
    fixed_clock.advance(minutes=16)
    fail(client, 1)
    after = user(engine)
    assert after.failed_login_count == 1 and after.locked_until is None


def test_success_resets_the_counter(client, engine, admin_id) -> None:
    fail(client, 3)
    assert login(client, "admin1", SECRET).status_code == 303
    assert user(engine).failed_login_count == 0


def test_lock_survives_recreating_the_app_on_the_same_file(client, engine, admin_id, db_file) -> None:
    fail(client, 5)
    fresh = build_app(db_file).test_client()
    assert login(fresh, "admin1", SECRET).status_code == 200


def test_attempts_while_locked_neither_count_nor_extend(client, engine, admin_id, fixed_clock) -> None:
    fail(client, 5)
    locked_state = user(engine)
    fixed_clock.advance(minutes=5)
    fail(client, 3)
    login(client, "admin1", SECRET)
    assert user(engine) == locked_state


def test_no_write_statement_is_issued_for_an_already_locked_account(client, engine, admin_id) -> None:  # NR-12
    fail(client, 5)
    statements: list[str] = []

    def spy(_conn, _cursor, statement, *_rest):  # type: ignore[no-untyped-def]
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", spy)
    try:
        login(client, "admin1", WRONG)
        login(client, "admin1", SECRET)
    finally:
        event.remove(Engine, "before_cursor_execute", spy)
    writes = [s for s in statements if s.lstrip().upper().startswith(("UPDATE", "INSERT", "DELETE"))]
    assert statements, "the spy saw no statements, so the test proves nothing"
    assert writes == []


def test_unknown_username_creates_no_rows_and_same_message(client, engine, admin_id) -> None:  # E-16
    with session_scope(engine) as s:
        before = s.scalar(select(func.count()).select_from(User))
    for _ in range(7):
        assert login(client, "ghost-user", WRONG).status_code == 200
    with session_scope(engine) as s:
        assert s.scalar(select(func.count()).select_from(User)) == before
    assert user(engine).failed_login_count == 0


def test_locked_account_stays_locked_after_the_correct_login_attempt(client, engine, admin_id) -> None:
    fail(client, 5)
    login(client, "admin1", SECRET)
    assert client.get("/employees/new").status_code == 302


@pytest.mark.parametrize("count", [1, 4])
def test_failures_below_the_limit_do_not_lock(client, engine, admin_id, count: int) -> None:
    fail(client, count)
    assert user(engine).locked_until is None and user(engine).failed_login_count == count
