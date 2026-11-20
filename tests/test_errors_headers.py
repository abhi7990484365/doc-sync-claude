"""TASK-024: response headers and error handlers (D-22, NFR-4, OQ-A15)."""

import logging

import pytest

from tests.conftest import add_user
from tests.web_helpers import build_app, page_token, post_employee, set_role, valid_form

LOGIN_LINK = 'href="/login"'


def assert_plain_error(response, status: int) -> None:  # type: ignore[no-untyped-def]
    body = response.get_data(as_text=True)
    assert response.status_code == status
    assert LOGIN_LINK in body
    assert "Traceback" not in body and "File \"" not in body


def test_unauthenticated_post_gives_401_page_without_www_authenticate(client) -> None:
    response = client.post("/employees/new", data=valid_form())
    assert_plain_error(response, 401)
    assert "WWW-Authenticate" not in response.headers


def test_wrong_role_gives_403_page(client, engine, admin_id) -> None:
    from tests.web_helpers import login
    from tests.conftest import login_secret_for_tests

    assert login(client, "admin1", login_secret_for_tests()).status_code == 303
    set_role(engine, admin_id, "someone_else")
    assert_plain_error(client.get("/employees/new"), 403)


def test_404_page_has_login_link(client) -> None:
    assert_plain_error(client.get("/does-not-exist"), 404)


def test_get_logout_is_405_page_and_does_not_log_out(logged_in) -> None:
    assert_plain_error(logged_in.get("/logout"), 405)
    assert logged_in.get("/employees/new").status_code == 200


def test_body_over_16_kb_gives_413_page(logged_in) -> None:
    token = page_token(logged_in, "/employees/new")
    form = valid_form(job_title="x" * (17 * 1024))
    response = post_employee(logged_in, form, token)
    assert_plain_error(response, 413)


def test_body_over_16_kb_unauthenticated_is_still_401(client) -> None:
    response = client.post("/employees/new", data=valid_form(job_title="x" * (17 * 1024)))
    assert response.status_code == 401


def test_unhandled_exception_gives_generic_500_page(logged_in, monkeypatch, caplog) -> None:
    def explode(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("internal-detail-xyz")

    monkeypatch.setattr("employee_app.routes.employee_routes.create_employee", explode)
    with caplog.at_level(logging.ERROR, logger="employee_app"):
        response = post_employee(logged_in, valid_form())
    assert_plain_error(response, 500)
    assert "internal-detail-xyz" not in response.get_data(as_text=True)
    assert any(r.exc_info for r in caplog.records)  # stack trace only in server log


@pytest.mark.parametrize("path", ["/login", "/does-not-exist"])
def test_security_headers_on_public_pages(client, path: str) -> None:
    headers = client.get(path).headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert "unsafe-inline" not in headers["Content-Security-Policy"]
    assert headers["Cache-Control"] == "no-store"


def test_no_store_on_authenticated_page_and_rerendered_form(logged_in) -> None:
    assert logged_in.get("/employees/new").headers["Cache-Control"] == "no-store"
    response = post_employee(logged_in, valid_form(email="bad"))
    assert response.status_code == 200 and response.headers["Cache-Control"] == "no-store"


def test_hsts_only_when_secure_mode_is_on(engine, db_file) -> None:
    secure = build_app(db_file, cookie_secure=True).test_client()
    assert "Strict-Transport-Security" in secure.get("/login", base_url="https://localhost").headers
    plain = build_app(db_file, cookie_secure=False).test_client()
    assert "Strict-Transport-Security" not in plain.get("/login").headers


def test_static_files_are_served_without_no_store_requirement(client) -> None:
    response = client.get("/static/style.css")
    assert response.status_code == 200 and response.headers["X-Content-Type-Options"] == "nosniff"


def test_slow_request_is_logged_over_threshold(engine, db_file, caplog) -> None:
    client = build_app(db_file, slow_request_seconds=1e-9).test_client()
    with caplog.at_level(logging.WARNING, logger="employee_app"):
        client.get("/login")
    assert any(r.getMessage().startswith("slow_request duration_ms=") for r in caplog.records)
