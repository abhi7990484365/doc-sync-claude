"""TASK-003 characterization tests: Flask, Flask-WTF, Flask-Login behaviour.

Each test pins a point the architecture marks "verify at implementation".
They use a tiny throw-away Flask app, not employee_app.
"""

import io
import re
import time

import pytest
from flask import Flask, abort, request, session
from flask_login import LoginManager, UserMixin, current_user, login_user
from flask_wtf.csrf import CSRFError, CSRFProtect, generate_csrf, validate_csrf
from wtforms import ValidationError

FAKE_KEY = "unit-test-only-key-not-a-secret"


class FakeUser(UserMixin):
    id = "1"


def make_app(*, check_default: bool = False, secure: bool = False, time_limit: int | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=FAKE_KEY,
        WTF_CSRF_CHECK_DEFAULT=check_default,
        WTF_CSRF_TIME_LIMIT=time_limit,
        SESSION_COOKIE_SECURE=secure,
        SESSION_COOKIE_SAMESITE="Lax",
        TESTING=False,
    )
    csrf = CSRFProtect(app)
    login = LoginManager(app)
    login.user_loader(lambda uid: FakeUser() if uid == "1" and session.get("ok") else None)
    app.extensions["test_csrf"] = csrf

    @app.errorhandler(CSRFError)
    def _csrf_error(_err: CSRFError):  # type: ignore[no-untyped-def]
        return "csrf", 403

    @app.before_request
    def _ordered_checks():  # type: ignore[no-untyped-def]
        if request.endpoint != "protected":
            return None
        if not current_user.is_authenticated:
            return "unauth", 401
        csrf.protect()
        return None

    @app.route("/protected", methods=["GET", "POST"])
    def protected():  # type: ignore[no-untyped-def]
        return "ok"

    @app.route("/login", methods=["GET", "POST"])
    def login_view():  # type: ignore[no-untyped-def]
        if request.method == "POST":
            csrf.protect()
            session["ok"] = True
            login_user(FakeUser())
            return "in"
        return generate_csrf()

    @app.route("/boom")
    def boom():  # type: ignore[no-untyped-def]
        abort(500)

    return app


def logged_in_client(app: Flask):  # type: ignore[no-untyped-def]
    client = app.test_client()
    token = client.get("/login").get_data(as_text=True)
    assert client.post("/login", data={"csrf_token": token}).status_code == 200
    return client


def test_a_automatic_check_can_be_disabled_and_manual_check_called() -> None:
    app = make_app(check_default=False)
    client = logged_in_client(app)
    # Manual check runs on /protected: missing token gives our 403, not 400.
    assert client.post("/protected", data={}).status_code == 403
    token = client.get("/login").get_data(as_text=True)
    assert client.post("/protected", data={"csrf_token": token}).status_code == 200


def test_a_default_automatic_check_returns_400_for_unauthenticated_callers() -> None:
    """Negative control: why D-5 is needed. With the default check on, an
    unauthenticated POST without a token is rejected by the extension first."""
    app = Flask(__name__)
    app.config.update(SECRET_KEY=FAKE_KEY)
    CSRFProtect(app)

    @app.route("/p", methods=["POST"])
    def p():  # type: ignore[no-untyped-def]
        return "ok"

    assert app.test_client().post("/p", data={}).status_code == 400


def test_b_authentication_runs_before_csrf_and_unauthenticated_gets_401() -> None:
    app = make_app()
    client = app.test_client()
    assert client.post("/protected", data={}).status_code == 401
    token = client.get("/login").get_data(as_text=True)
    assert client.post("/protected", data={"csrf_token": token}).status_code == 401


def test_b_request_body_is_not_read_for_unauthenticated_requests() -> None:
    class Spy(io.BytesIO):
        reads = 0

        def read(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            Spy.reads += 1
            return super().read(*args, **kwargs)

        readline = read  # type: ignore[assignment]

    app = make_app()
    body = b"first_name=A&last_name=B"
    stream = Spy(body)
    response = app.test_client().post(
        "/protected",
        input_stream=stream,
        content_length=len(body),
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 401
    assert Spy.reads == 0


def test_b_authenticated_without_token_is_403() -> None:
    client = logged_in_client(make_app())
    assert client.post("/protected", data={}).status_code == 403


def test_b_public_login_post_without_token_is_403() -> None:
    assert make_app().test_client().post("/login", data={}).status_code == 403


def test_c_token_lifetime_none_means_session_lifetime_and_int_limit_expires(monkeypatch: pytest.MonkeyPatch) -> None:
    for limit, expect_valid in ((None, True), (3600, False)):
        app = make_app(time_limit=limit)
        with app.test_request_context("/"):
            token = generate_csrf()
            real = time.time
            monkeypatch.setattr(time, "time", lambda: real() + 9 * 3600)
            try:
                if expect_valid:
                    validate_csrf(token, time_limit=limit)
                else:
                    with pytest.raises(ValidationError):
                        validate_csrf(token, time_limit=limit)
            finally:
                monkeypatch.setattr(time, "time", real)


def test_c_library_default_time_limit_is_3600_not_session_lifetime() -> None:
    """The library default differs from the architecture, so it must be set."""
    app = Flask(__name__)
    app.config.update(SECRET_KEY=FAKE_KEY)
    CSRFProtect(app)
    assert app.config.get("WTF_CSRF_TIME_LIMIT", 3600) == 3600


def set_cookies(response) -> list[str]:  # type: ignore[no-untyped-def]
    return response.headers.getlist("Set-Cookie")


def test_d_remember_me_cookie_is_not_issued() -> None:
    app = make_app()
    client = app.test_client()
    token = client.get("/login").get_data(as_text=True)
    response = client.post("/login", data={"csrf_token": token})
    cookies = " ".join(set_cookies(response))
    assert "remember_token" not in cookies
    assert "session=" in cookies


@pytest.mark.parametrize("secure", [True, False])
def test_e_cookie_flags(secure: bool) -> None:
    app = make_app(secure=secure)
    client = app.test_client()
    https = "https://localhost"
    token = client.get("/login", base_url=https).get_data(as_text=True)
    response = client.post(
        "/login", data={"csrf_token": token}, base_url=https, headers={"Referer": https + "/login"}
    )
    cookie = [c for c in set_cookies(response) if c.startswith("session=")][0]
    assert "HttpOnly" in cookie
    assert re.search(r"SameSite=Lax", cookie)
    assert ("Secure" in cookie) is secure


def test_e_https_post_without_referer_is_rejected_by_strict_ssl_check() -> None:
    """Extra finding: over HTTPS (as the app sees it) Flask-WTF also requires a
    same-origin Referer header (WTF_CSRF_SSL_STRICT, default on)."""
    app = make_app()
    client = app.test_client()
    https = "https://localhost"
    token = client.get("/login", base_url=https).get_data(as_text=True)
    assert client.post("/login", data={"csrf_token": token}, base_url=https).status_code == 403
