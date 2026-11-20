"""TASK-026: ordered CSRF enforcement (AC-08b, D-5)."""

from employee_app.db.users import find_user_by_username
from tests.web_helpers import employee_counts, page_token, post_employee, valid_form


def test_unauthenticated_post_without_token_is_401(client, engine) -> None:
    assert client.post("/employees/new", data=valid_form()).status_code == 401
    assert employee_counts(engine) == (0, 0)


def test_unauthenticated_post_with_a_valid_token_is_still_401(client, engine) -> None:
    token = page_token(client, "/login")
    assert post_employee(client, valid_form(), token).status_code == 401
    assert employee_counts(engine) == (0, 0)


def test_authenticated_post_without_token_is_403_and_no_record(logged_in, engine) -> None:
    assert logged_in.post("/employees/new", data=valid_form()).status_code == 403
    assert employee_counts(engine) == (0, 0)


def test_authenticated_post_with_wrong_token_is_403(logged_in, engine) -> None:
    assert post_employee(logged_in, valid_form(), "not-a-token").status_code == 403
    assert employee_counts(engine) == (0, 0)


def test_login_post_without_token_is_403_and_counter_unchanged(client, engine, admin_id) -> None:
    response = client.post("/login", data={"username": "admin1", "password": "wrong-guess-value"})
    assert response.status_code == 403
    assert find_user_by_username(engine, "admin1").failed_login_count == 0


def test_login_post_with_wrong_token_is_403_and_counter_unchanged(client, engine, admin_id) -> None:
    response = client.post("/login", data={"csrf_token": "bad", "username": "admin1", "password": "x"})
    assert response.status_code == 403
    assert find_user_by_username(engine, "admin1").failed_login_count == 0


def test_unauthenticated_logout_post_is_401(client) -> None:
    assert client.post("/logout").status_code == 401
