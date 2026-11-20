"""TASK-029: logout (FR-14, AC-15, P-11, N-15, N-16, OQ-A10)."""

from employee_app.db.users import find_user_by_username
from tests.conftest import login_secret_for_tests
from tests.web_helpers import login, page_token

SECRET = login_secret_for_tests()


def logout(client, token: str | None = None):  # type: ignore[no-untyped-def]
    token = token if token is not None else page_token(client, "/employees/new")
    return client.post("/logout", data={"csrf_token": token})


def test_logout_ends_the_session_and_old_cookie_is_rejected(logged_in, app) -> None:  # P-11
    old_cookie = logged_in.get_cookie("session")
    response = logout(logged_in)
    assert response.status_code == 303 and response.headers["Location"].endswith("/login")
    assert logged_in.get("/employees/new").status_code == 302
    replay = app.test_client()
    replay.set_cookie("session", old_cookie.value)
    assert replay.get("/employees/new").status_code == 302


def test_logout_increments_auth_version_once(logged_in, engine) -> None:
    logout(logged_in)
    assert find_user_by_username(engine, "admin1").auth_version == 1


def test_missing_token_gives_403_and_does_not_log_out(logged_in, engine) -> None:  # N-16
    assert logged_in.post("/logout").status_code == 403
    assert find_user_by_username(engine, "admin1").auth_version == 0
    assert logged_in.get("/employees/new").status_code == 200


def test_get_logout_does_not_log_out(logged_in, engine) -> None:
    assert logged_in.get("/logout").status_code == 405
    assert logged_in.get("/employees/new").status_code == 200
    assert find_user_by_username(engine, "admin1").auth_version == 0


def test_stale_session_logout_is_401_with_no_increment(logged_in, engine, app) -> None:
    token = page_token(logged_in, "/employees/new")
    other = app.test_client()
    login(other, "admin1", SECRET)
    logout(other)  # ends every session of the user
    assert find_user_by_username(engine, "admin1").auth_version == 1
    assert logout(logged_in, token).status_code == 401
    assert find_user_by_username(engine, "admin1").auth_version == 1


def test_logout_ends_other_sessions_of_the_same_user(logged_in, app) -> None:
    other = app.test_client()
    login(other, "admin1", SECRET)
    assert other.get("/employees/new").status_code == 200
    logout(logged_in)
    assert other.get("/employees/new").status_code == 302


def test_unauthenticated_logout_is_401(client, engine, admin_id) -> None:
    assert client.post("/logout").status_code == 401
    assert find_user_by_username(engine, "admin1").auth_version == 0
