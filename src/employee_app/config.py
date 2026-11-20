"""C-7 Configuration: environment variables plus an optional non-secret file.

Two groups are validated separately (D-24):

* core / database group (``load_core_settings``): needs only the database
  location; used by the operator commands.
* web group (``load_web_settings``): adds signing key, cookie security,
  environment mode and the department list.

Error messages name the setting and never print a value. Passwords are never
read from the environment. Environment variable names are a Proposal.
"""

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from employee_app.validation.limits import ValidationLimits

ENV_DB_PATH = "EMPLOYEE_APP_DB_PATH"
ENV_SECRET_KEY = "EMPLOYEE_APP_SECRET_KEY"
ENV_COOKIE_SECURE = "EMPLOYEE_APP_COOKIE_SECURE"
ENV_MODE = "EMPLOYEE_APP_ENV"
ENV_SETTINGS_FILE = "EMPLOYEE_APP_SETTINGS_FILE"

MODES = ("development", "production", "testing")
NOT_FOUND = "Not Found"


class ConfigError(Exception):
    """A setting is missing or invalid. The message names the setting only."""


@dataclass(frozen=True)
class DatabaseSettings:
    database_path: str
    busy_timeout_seconds: float = 2.0


@dataclass(frozen=True)
class LockoutSettings:
    max_failures: int = 5
    lock_minutes: int = 15


@dataclass(frozen=True)
class CoreSettings:
    """Everything the operator commands and the services need."""

    database: DatabaseSettings
    limits: ValidationLimits = field(default_factory=ValidationLimits)
    lockout: LockoutSettings = field(default_factory=LockoutSettings)
    password_min_length: int = 12


@dataclass(frozen=True)
class WebSettings:
    core: CoreSettings
    secret_key: str = field(repr=False)
    cookie_secure: bool
    mode: str
    departments: tuple[str, ...]
    body_max_bytes: int = 16 * 1024
    session_lifetime_seconds: int = 8 * 3600
    csrf_lifetime_seconds: int = 8 * 3600
    trusted_proxy_count: int = 0
    slow_request_seconds: float = 3.0


def _int_setting(source: Mapping[str, Any], name: str, default: int | None, minimum: int = 1) -> int | None:
    value = source.get(name, default)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"Setting {name} is invalid")
    return value


def _number_setting(source: Mapping[str, Any], name: str, default: float) -> float:
    value = source.get(name, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ConfigError(f"Setting {name} is invalid")
    return float(value)


def load_settings_file(env: Mapping[str, str]) -> dict[str, Any]:
    """Read the optional non-secret JSON settings file; empty dict when unset."""
    path = env.get(ENV_SETTINGS_FILE, "").strip()
    if not path:
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"Setting {ENV_SETTINGS_FILE} is invalid (file unreadable or not JSON)") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Setting {ENV_SETTINGS_FILE} is invalid (not an object)")
    return data


def _database_settings(env: Mapping[str, str], file: Mapping[str, Any]) -> DatabaseSettings:
    path = env.get(ENV_DB_PATH, "").strip()
    if not path:
        raise ConfigError(f"Setting {ENV_DB_PATH} is missing")
    return DatabaseSettings(path, _number_setting(file, "busy_timeout_seconds", 2.0))


def load_core_settings(env: Mapping[str, str] | None = None) -> CoreSettings:
    """Database group: requires only the database location (D-24)."""
    env = os.environ if env is None else env
    file = load_settings_file(env)
    return CoreSettings(
        database=_database_settings(env, file),
        limits=ValidationLimits(
            name_max_length=_int_setting(file, "name_max_length", 100),  # type: ignore[arg-type]
            email_max_length=_int_setting(file, "email_max_length", 254),  # type: ignore[arg-type]
            max_future_days=_int_setting(file, "max_future_days", None, minimum=0),
        ),
        lockout=LockoutSettings(
            max_failures=_int_setting(file, "lockout_max_failures", 5),  # type: ignore[arg-type]
            lock_minutes=_int_setting(file, "lockout_minutes", 15),  # type: ignore[arg-type]
        ),
        password_min_length=_int_setting(file, "password_min_length", 12),  # type: ignore[arg-type]
    )


def _parse_cookie_secure(env: Mapping[str, str]) -> bool:
    raw = env.get(ENV_COOKIE_SECURE, "1").strip().lower()
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    raise ConfigError(f"Setting {ENV_COOKIE_SECURE} is invalid")


def _parse_mode(env: Mapping[str, str]) -> str:
    mode = env.get(ENV_MODE, "").strip().lower()
    if not mode:
        raise ConfigError(f"Setting {ENV_MODE} is missing")
    if mode not in MODES:
        raise ConfigError(f"Setting {ENV_MODE} is invalid")
    return mode


def _parse_departments(file: Mapping[str, Any]) -> tuple[str, ...]:
    raw = file.get("departments", [])
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ConfigError("Setting departments is invalid")
    return tuple(item.strip() for item in raw if item.strip())


def load_web_settings(env: Mapping[str, str] | None = None) -> WebSettings:
    """Web group: core settings plus web-only settings. The department list
    defaults to empty (names are Not Found); emptiness is refused at startup
    outside testing (see app factory)."""
    env = os.environ if env is None else env
    file = load_settings_file(env)
    core = load_core_settings(env)
    secret = env.get(ENV_SECRET_KEY, "")
    if not secret:
        raise ConfigError(f"Setting {ENV_SECRET_KEY} is missing")
    session_seconds = _int_setting(file, "session_lifetime_hours", 8) * 3600  # type: ignore[operator]
    csrf_hours = _int_setting(file, "csrf_lifetime_hours", None)
    return WebSettings(
        core=core,
        secret_key=secret,
        cookie_secure=_parse_cookie_secure(env),
        mode=_parse_mode(env),
        departments=_parse_departments(file),
        body_max_bytes=_int_setting(file, "body_max_bytes", 16 * 1024),  # type: ignore[arg-type]
        session_lifetime_seconds=session_seconds,
        csrf_lifetime_seconds=session_seconds if csrf_hours is None else csrf_hours * 3600,
        trusted_proxy_count=_int_setting(file, "trusted_proxy_count", 0, minimum=0),  # type: ignore[arg-type]
        slow_request_seconds=_number_setting(file, "slow_request_seconds", 3.0),
    )
