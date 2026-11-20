"""Flask extension singletons and the per-app state container."""

from dataclasses import dataclass

from flask import current_app
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.engine import Engine

from employee_app.config import WebSettings

login_manager = LoginManager()
csrf = CSRFProtect()

STATE_KEY = "employee_app"


@dataclass(frozen=True)
class AppState:
    settings: WebSettings
    engine: Engine


def get_state() -> AppState:
    """Return the settings and engine of the current app."""
    return current_app.extensions[STATE_KEY]  # type: ignore[no-any-return]
