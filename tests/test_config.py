"""TASK-006: configuration defaults, grouping, failure messages."""

import json
from pathlib import Path

import pytest

from employee_app import config
from employee_app.config import ConfigError, load_core_settings, load_web_settings

FAKE_SECRET = "fake-signing-key-for-tests-only-0123456789"


def web_env(tmp_path: Path, **extra: str) -> dict[str, str]:
    env = {
        config.ENV_DB_PATH: str(tmp_path / "x.sqlite3"),
        config.ENV_SECRET_KEY: FAKE_SECRET,
        config.ENV_MODE: "testing",
    }
    env.update(extra)
    return env


def test_defaults_match_the_architecture_table(tmp_path: Path) -> None:
    s = load_web_settings(web_env(tmp_path))
    assert (s.core.limits.name_max_length, s.core.limits.email_max_length) == (100, 254)
    assert s.body_max_bytes == 16 * 1024
    assert s.core.limits.max_future_days is None
    assert (s.core.lockout.max_failures, s.core.lockout.lock_minutes) == (5, 15)
    assert s.core.password_min_length == 12
    assert s.session_lifetime_seconds == 8 * 3600
    assert s.csrf_lifetime_seconds == s.session_lifetime_seconds
    assert s.core.database.busy_timeout_seconds == 2.0
    assert s.trusted_proxy_count == 0
    assert s.slow_request_seconds == 3.0
    assert s.cookie_secure is True
    assert s.departments == ()


def test_operator_group_requires_only_database_location(tmp_path: Path) -> None:
    core = load_core_settings({config.ENV_DB_PATH: str(tmp_path / "x.db")})
    assert core.database.database_path.endswith("x.db")


def test_missing_database_location_names_the_setting() -> None:
    with pytest.raises(ConfigError, match=config.ENV_DB_PATH):
        load_core_settings({})


@pytest.mark.parametrize("missing", [config.ENV_SECRET_KEY, config.ENV_MODE])
def test_missing_web_setting_names_the_setting(tmp_path: Path, missing: str) -> None:
    env = web_env(tmp_path)
    del env[missing]
    with pytest.raises(ConfigError, match=missing):
        load_web_settings(env)


def test_web_settings_not_needed_by_commands(tmp_path: Path) -> None:
    # no signing key, mode or department list: the core group still loads
    load_core_settings({config.ENV_DB_PATH: str(tmp_path / "x.db")})


@pytest.mark.parametrize(("name", "value"), [(config.ENV_MODE, "staging"), (config.ENV_COOKIE_SECURE, "maybe")])
def test_invalid_values_fail_naming_setting_without_value(tmp_path: Path, name: str, value: str) -> None:
    with pytest.raises(ConfigError) as caught:
        load_web_settings(web_env(tmp_path, **{name: value}))
    assert name in str(caught.value) and value not in str(caught.value)


def test_cookie_secure_can_be_turned_off_explicitly(tmp_path: Path) -> None:
    assert load_web_settings(web_env(tmp_path, **{config.ENV_COOKIE_SECURE: "0"})).cookie_secure is False


def write_settings(tmp_path: Path, data: object) -> str:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_settings_file_overrides_defaults_and_supplies_departments(tmp_path: Path) -> None:
    file = write_settings(tmp_path, {"departments": ["Test A", " Test B "], "lockout_max_failures": 3,
                                     "session_lifetime_hours": 1, "max_future_days": 30})
    s = load_web_settings(web_env(tmp_path, **{config.ENV_SETTINGS_FILE: file}))
    assert s.departments == ("Test A", "Test B")
    assert s.core.lockout.max_failures == 3
    assert s.session_lifetime_seconds == 3600 and s.csrf_lifetime_seconds == 3600
    assert s.core.limits.max_future_days == 30


@pytest.mark.parametrize("data", [{"lockout_max_failures": 0}, {"lockout_max_failures": "5"},
                                  {"body_max_bytes": True}, {"departments": "Sales"},
                                  {"departments": [1]}, {"busy_timeout_seconds": -1}, []])
def test_invalid_settings_file_values_fail_fast(tmp_path: Path, data: object) -> None:
    file = write_settings(tmp_path, data)
    with pytest.raises(ConfigError):
        load_web_settings(web_env(tmp_path, **{config.ENV_SETTINGS_FILE: file}))


def test_settings_file_missing_or_not_json_fails_without_leaking_path(tmp_path: Path) -> None:
    missing = str(tmp_path / "nope.json")
    with pytest.raises(ConfigError) as caught:
        load_web_settings(web_env(tmp_path, **{config.ENV_SETTINGS_FILE: missing}))
    assert missing not in str(caught.value)
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_core_settings({config.ENV_DB_PATH: "x", config.ENV_SETTINGS_FILE: str(bad)})


def test_error_messages_never_contain_secret_values(tmp_path: Path) -> None:
    env = web_env(tmp_path, **{config.ENV_MODE: "bogus"})
    with pytest.raises(ConfigError) as caught:
        load_web_settings(env)
    assert FAKE_SECRET not in str(caught.value)


def test_secret_not_in_repr(tmp_path: Path) -> None:
    assert FAKE_SECRET not in repr(load_web_settings(web_env(tmp_path)))


def test_no_environment_variable_name_refers_to_a_password() -> None:
    names = [value for key, value in vars(config).items() if key.startswith("ENV_")]
    assert names and not any("PASSWORD" in name.upper() for name in names)
