"""TASK-023: app factory and web-only startup checks (D-24)."""

from pathlib import Path

import pytest
from sqlalchemy import text

from employee_app import config
from employee_app.app import StartupError, create_app
from employee_app.config import ConfigError, load_web_settings
from tests.conftest import make_engine
from tests.web_helpers import FAKE_SIGNING_KEY, build_app, page_token, web_settings


def test_app_starts_on_verified_schema(engine, db_file) -> None:
    app = build_app(db_file)
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_secure_cookie_setting_is_applied(engine, db_file) -> None:
    assert build_app(db_file, cookie_secure=True).config["SESSION_COOKIE_SECURE"] is True


def test_csrf_protection_is_enabled_in_the_test_configuration(engine, db_file) -> None:
    app = build_app(db_file)
    assert app.config["WTF_CSRF_ENABLED"] is True
    client = app.test_client()
    assert client.post("/login", data={"username": "a", "password": "b"}).status_code == 403
    assert page_token(client)  # token is issued on the form


def test_body_limit_and_csrf_lifetime_follow_settings(engine, db_file) -> None:
    app = build_app(db_file)
    assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024
    assert app.config["WTF_CSRF_TIME_LIMIT"] == 8 * 3600


def test_schema_without_unique_index_fails_startup(engine, db_file) -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP INDEX ux_employee_email_normalized"))
    with pytest.raises(StartupError, match=r"employee\.email_normalized"):
        build_app(db_file)


def test_empty_database_fails_startup_naming_tables(db_file) -> None:
    with pytest.raises(StartupError, match="init-db"):
        build_app(db_file)


def test_unreachable_database_fails_startup(tmp_path) -> None:
    with pytest.raises(StartupError, match="not reachable"):
        build_app(tmp_path / "missing" / "x.sqlite3")


def test_empty_department_list_fails_outside_tests(engine, db_file) -> None:
    with pytest.raises(StartupError, match="departments"):
        build_app(db_file, departments=(), mode="production")


def test_empty_department_list_allowed_in_testing_mode(engine, db_file) -> None:
    build_app(db_file, departments=(), mode="testing")


def test_debug_refused_outside_development(engine, db_file) -> None:
    with pytest.raises(StartupError, match="Debug"):
        create_app(web_settings(db_file, mode="production"), {"DEBUG": True})


def test_debug_refused_through_flask_debug_environment(engine, db_file, monkeypatch) -> None:
    monkeypatch.setenv("FLASK_DEBUG", "1")
    with pytest.raises(StartupError, match="Debug"):
        build_app(db_file, mode="production")


def test_debug_allowed_in_development(engine, db_file) -> None:
    create_app(web_settings(db_file, mode="development"), {"DEBUG": True})


def test_missing_signing_key_fails_fast_naming_setting(db_file) -> None:
    env = {config.ENV_DB_PATH: str(db_file), config.ENV_MODE: "testing"}
    with pytest.raises(ConfigError, match=config.ENV_SECRET_KEY):
        load_web_settings(env)


def test_startup_messages_contain_no_secret(engine, db_file) -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP INDEX ux_user_username_normalized"))
    with pytest.raises(StartupError) as caught:
        build_app(db_file)
    assert FAKE_SIGNING_KEY not in str(caught.value)


def test_commands_do_not_need_the_web_checks(db_file) -> None:
    """The web app refuses this database (no schema) but the commands context
    with require_schema=False works without any web setting."""
    from employee_app.commands.context import build_context

    ctx = build_context({config.ENV_DB_PATH: str(db_file)}, require_schema=False)
    assert make_engine(db_file) is not None and ctx.settings.database.database_path == str(db_file)
