"""C-1 App factory and web-only startup checks (D-24).

Web-only checks (the operator commands never run these): database reachable,
schema verified before serving, signing key present, cookie security and mode
valid, debug refused outside development, department list non-empty outside
testing. Messages name the setting or object and never print values.
"""

import logging
import os
from collections.abc import Mapping
from typing import Any

from flask import Flask
from sqlalchemy.engine import Engine
from werkzeug.middleware.proxy_fix import ProxyFix

from employee_app.auth.loader import load_user
from employee_app.config import ConfigError, WebSettings, load_web_settings
from employee_app.db.engine import check_reachable, create_db_engine
from employee_app.db.errors import SchemaVerificationError, StorageError
from employee_app.db.verify import verify_schema
from employee_app.extensions import STATE_KEY, AppState, csrf, login_manager
from employee_app.logging_setup import configure_logging, log_event
from employee_app.routes import auth_routes, employee_routes, errors

TRUTHY = ("1", "true", "yes", "on")


class StartupError(Exception):
    """A web startup check failed. The message names the setting or object."""


def _debug_requested(overrides: Mapping[str, Any] | None) -> bool:
    if overrides and overrides.get("DEBUG"):
        return True
    return os.environ.get("FLASK_DEBUG", "").strip().lower() in TRUTHY


def check_settings(settings: WebSettings, debug: bool) -> None:
    """Settings-level startup checks (no database access)."""
    if debug and settings.mode != "development":
        raise StartupError("Debug mode is refused outside development (setting EMPLOYEE_APP_ENV)")
    if not settings.departments and settings.mode != "testing":
        raise StartupError("Setting departments is empty; the department list is required")


def check_database(engine: Engine) -> None:
    """Database reachable and schema verified before serving."""
    try:
        check_reachable(engine)
        verify_schema(engine)
    except StorageError as exc:
        raise StartupError(f"Database is not reachable ({exc.category})") from None
    except SchemaVerificationError as exc:
        raise StartupError(f"{exc}. Run init-db first.") from None


def _configure_flask(app: Flask, settings: WebSettings) -> None:
    lifetime = settings.session_lifetime_seconds
    app.config.update(
        SECRET_KEY=settings.secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.cookie_secure,
        PERMANENT_SESSION_LIFETIME=lifetime,
        MAX_CONTENT_LENGTH=settings.body_max_bytes,
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_CHECK_DEFAULT=False,  # C-2 runs the check after authentication (D-5)
        WTF_CSRF_TIME_LIMIT=settings.csrf_lifetime_seconds,
    )
    if settings.trusted_proxy_count:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=settings.trusted_proxy_count)  # type: ignore[method-assign]


def create_app(
    settings: WebSettings | None = None, overrides: Mapping[str, Any] | None = None
) -> Flask:
    """Build the Flask app. Raises ConfigError or StartupError on bad setup."""
    settings = settings or load_web_settings()
    check_settings(settings, _debug_requested(overrides))
    engine = create_db_engine(settings.core.database)
    check_database(engine)
    app = Flask(__name__)
    _configure_flask(app, settings)
    app.config.update(overrides or {})
    app.extensions[STATE_KEY] = AppState(settings=settings, engine=engine)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(employee_routes.bp)
    errors.register(app, hsts=settings.cookie_secure, slow_seconds=settings.slow_request_seconds)
    configure_logging()
    log_event(logging.INFO, "app_started")
    return app


__all__ = ["ConfigError", "StartupError", "create_app"]
