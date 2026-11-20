"""TASK-025: per-request session validation (NFR-1, D-16, E-12)."""

from datetime import timedelta

import pytest
from sqlalchemy import delete

from employee_app.db.engine import session_scope
from employee_app.db.models import User
from employee_app.db.users import deactivate_user_by_id, increment_auth_version
from tests.conftest import login_secret_for_tests
from tests.web_helpers import login, page_token, post_employee, valid_form


def remove_user(engine, uid, clock) -> None:  # type: ignore[no-untyped-def]
    with session_scope(engine, write=True) as s:
        s.execute(delete(User).where(User.id == uid))
        s.commit()


def deactivate(engine, uid, clock) -> None:  # type: ignore[no-untyped-def]
    deactivate_user_by_id(engine, uid)


def bump_version(engine, uid, clock) -> None:  # type: ignore[no-untyped-def]
    increment_auth_version(engine, uid)


def expire(engine, uid, clock) -> None:  # type: ignore[no-untyped-def]
    clock.advance(hours=8, seconds=1)


CAUSES = [("user_missing", remove_user), ("inactive", deactivate), ("auth_version", bump_version),
          ("lifetime", expire)]


def test_valid_session_is_accepted(logged_in) -> None:
    assert logged_in.get("/employees/new").status_code == 200


@pytest.mark.parametrize(("name", "mutate"), CAUSES, ids=[c[0] for c in CAUSES])
def test_page_request_redirects_when_session_rejected(logged_in, engine, admin_id, fixed_clock, name, mutate) -> None:
    mutate(engine, admin_id, fixed_clock)
    response = logged_in.get("/employees/new")
    assert response.status_code == 302 and response.headers["Location"].endswith("/login")


@pytest.mark.parametrize(("name", "mutate"), CAUSES, ids=[c[0] for c in CAUSES])
def test_submission_gets_401_and_creates_nothing(logged_in, engine, admin_id, fixed_clock, name, mutate) -> None:
    from tests.web_helpers import employee_counts

    token = page_token(logged_in, "/employees/new")
    mutate(engine, admin_id, fixed_clock)
    assert post_employee(logged_in, valid_form(), token).status_code == 401
    assert employee_counts(engine) == (0, 0)


def test_session_valid_just_inside_the_lifetime(logged_in, fixed_clock) -> None:
    fixed_clock.advance(hours=8)  # exactly the maximum is still allowed
    assert logged_in.get("/employees/new").status_code == 200


def test_remember_me_cookie_is_not_issued(client, admin_id) -> None:
    response = login(client, "admin1", login_secret_for_tests())
    cookies = " ".join(response.headers.getlist("Set-Cookie"))
    assert "remember_token" not in cookies and "session=" in cookies


def test_tampered_session_cookie_is_unauthenticated(client, admin_id) -> None:
    login(client, "admin1", login_secret_for_tests())
    client.set_cookie("session", "garbage.value.here")
    assert client.get("/employees/new").status_code == 302


def test_session_from_the_future_is_rejected(logged_in, fixed_clock) -> None:
    fixed_clock.advance(hours=-1)  # clock moved before the issue time
    assert logged_in.get("/employees/new").status_code == 302


def test_clock_advance_helper_is_used(fixed_clock) -> None:
    before = fixed_clock.now
    fixed_clock.advance(minutes=1)
    assert fixed_clock.now - before == timedelta(minutes=1)
