"""TASK-039: security tests (NFR-2, NFR-4, D-21, D-22)."""

import logging
import secrets

import pytest
from employee_app.db.engine import create_db_engine
from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.conftest import login_secret_for_tests
from tests.web_helpers import build_app, login, post_employee, valid_form

KNOWN_EMAIL = "known.address.7731@example.com"
KNOWN_NAME = "Zephyrine"
WRONG = "definitely-not-the-login-value"


def test_logs_contain_no_secret_username_hash_or_employee_value(client, admin_id, engine, monkeypatch, caplog) -> None:
    from employee_app.db.users import find_user_by_username

    stored_hash = find_user_by_username(engine, "admin1").password_hash
    caplog.set_level(logging.DEBUG)
    login(client, "admin1", WRONG)
    for _ in range(5):
        login(client, "admin1", WRONG)  # failed logins and lockout
    login(client, "no-such-user", WRONG)
    from employee_app.db.lockout import unlock
    unlock(engine, admin_id)
    assert login(client, "admin1", login_secret_for_tests()).status_code == 303
    ok = post_employee(client, valid_form(first_name=KNOWN_NAME, email=KNOWN_EMAIL))
    assert ok.status_code == 303
    # provoked storage error with a known email: pre-check bypassed so the unique index fires
    monkeypatch.setattr("employee_app.services.employee._pre_check", lambda *_a: False)
    monkeypatch.setattr("employee_app.services.employee.email_exists", lambda *_a: False)
    assert post_employee(client, valid_form(first_name=KNOWN_NAME, email=KNOWN_EMAIL)).status_code == 500
    text = caplog.text
    for forbidden in ("admin1", "no-such-user", WRONG, login_secret_for_tests(), stored_hash, KNOWN_EMAIL,
                      KNOWN_NAME, "5551234567", "scrypt:", "csrf_token"):
        assert forbidden not in text, forbidden
    assert "login_failure" in text and "account_locked" in text and "employee_created" in text


def test_account_creation_logs_no_username_or_secret(db_file, engine, caplog) -> None:
    secret = secrets.token_urlsafe(18)
    with caplog.at_level(logging.DEBUG):
        run_cli(["create-user"], cmd_env(db_file), create_user_input("visible.name", secret))
    assert "visible.name" not in caplog.text and secret not in caplog.text


def test_storage_exception_text_hides_statement_parameters(db_file, engine) -> None:
    from employee_app.config import DatabaseSettings
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    eng = create_db_engine(DatabaseSettings(str(db_file)))
    with eng.begin() as conn:
        conn.execute(text("INSERT INTO employee (first_name,last_name,email,email_normalized,phone,department,"
                          "job_title,joining_date) VALUES ('a','b',:e,:e,'5551234567','d','j','2026-11-20')"),
                     {"e": KNOWN_EMAIL})
    with pytest.raises(IntegrityError) as caught:
        with eng.begin() as conn:
            conn.execute(text("INSERT INTO employee (first_name,last_name,email,email_normalized,phone,"
                              "department,job_title,joining_date) VALUES ('a','b',:e,:e,'5551234567','d','j',"
                              "'2026-11-20')"), {"e": KNOWN_EMAIL})
    assert KNOWN_EMAIL not in str(caught.value)


@pytest.mark.parametrize("secure", [True, False])
def test_cookie_flags(engine, db_file, admin_id, fixed_clock, secure: bool) -> None:
    client = build_app(db_file, cookie_secure=secure).test_client()
    https = "https://localhost"
    token = page_token_https(client, https)
    response = client.post("/login", base_url=https, headers={"Referer": https + "/login"},
                           data={"csrf_token": token, "username": "admin1", "password": login_secret_for_tests()})
    cookie = next(c for c in response.headers.getlist("Set-Cookie") if c.startswith("session="))
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie and ("Secure" in cookie) is secure


def page_token_https(client, base: str) -> str:  # type: ignore[no-untyped-def]
    from tests.web_helpers import csrf_token

    return csrf_token(client.get("/login", base_url=base).get_data(as_text=True))


SECURITY_HEADERS = ("X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy", "Cache-Control")


def test_headers_on_authenticated_failed_form_login_and_error_pages(logged_in, app) -> None:
    responses = [
        logged_in.get("/employees/new"),
        post_employee(logged_in, valid_form(email="bad")),
        logged_in.get("/login"),
        logged_in.post("/employees/new", data=valid_form()),        # 403 no token
        post_employee(logged_in, valid_form(job_title="x" * (17 * 1024))),  # 413
    ]
    anon = app.test_client()
    anonymous = [anon.get("/login"), anon.post("/employees/new", data=valid_form())]  # 401
    for response in responses + anonymous:
        for header in SECURITY_HEADERS:
            assert header in response.headers, (response.status_code, header)
        assert response.headers["Cache-Control"] == "no-store"
    assert [r.status_code for r in responses[3:]] == [403, 413]
    assert anonymous[1].status_code == 401


def test_error_pages_contain_no_stack_text(logged_in) -> None:
    for response in (logged_in.get("/nope"), logged_in.get("/logout"),
                     logged_in.post("/employees/new", data=valid_form())):
        text = response.get_data(as_text=True)
        assert "Traceback" not in text and "werkzeug" not in text.lower() and "flask" not in text.lower()


def test_debug_refused_outside_development(engine, db_file) -> None:
    from employee_app.app import StartupError, create_app
    from tests.web_helpers import web_settings

    with pytest.raises(StartupError):
        create_app(web_settings(db_file, mode="production"), {"DEBUG": True})


def test_password_hash_is_never_rendered_or_returned(logged_in, engine) -> None:
    from employee_app.db.users import find_user_by_username

    stored = find_user_by_username(engine, "admin1").password_hash
    assert stored not in logged_in.get("/employees/new").get_data(as_text=True)


def test_session_cookie_does_not_contain_the_secret_or_hash(logged_in, engine) -> None:
    cookie = logged_in.get_cookie("session").value
    assert login_secret_for_tests() not in cookie


def test_engine_hides_parameters_setting() -> None:
    from employee_app.config import DatabaseSettings

    assert create_db_engine(DatabaseSettings("x.db")).hide_parameters is True
