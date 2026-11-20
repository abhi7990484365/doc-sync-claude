"""Shared fixtures. Test data is synthetic; no real personal data.

Throw-away credentials are generated per test run with ``secrets``.
"""

import secrets
from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from functools import cache
from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

from employee_app import clock
from employee_app.config import DatabaseSettings
from employee_app.db import create_schema
from employee_app.db.engine import create_db_engine
from employee_app.db.users import insert_user
from employee_app.security import hash_password
from employee_app.validation.username import normalize_username

DEFAULT_NOW = datetime(2026, 11, 20, 12, 0, 0, tzinfo=timezone.utc)


class FixedClock:
    """Mutable fake clock that pins both the local date and the UTC time."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def utc_now(self) -> datetime:
        return self.now

    def today_local(self) -> date:
        return self.now.date()

    def advance(self, **kwargs: float) -> None:
        self.now = self.now + timedelta(**kwargs)


@pytest.fixture
def fixed_clock(monkeypatch: pytest.MonkeyPatch) -> FixedClock:
    fake = FixedClock(DEFAULT_NOW)
    monkeypatch.setattr(clock, "utc_now", fake.utc_now)
    monkeypatch.setattr(clock, "today_local", fake.today_local)
    return fake


# ---------------------------------------------------------------- database
@cache
def login_secret_for_tests() -> str:
    """Throw-away login value for the whole test run (generated, not stored)."""
    return secrets.token_urlsafe(18)


@cache
def _test_hash() -> str:
    return hash_password(login_secret_for_tests())


def make_engine(path: Path, busy: float = 2.0) -> Engine:
    return create_db_engine(DatabaseSettings(str(path), busy))


@pytest.fixture
def db_file(tmp_path: Path) -> Path:
    return tmp_path / "test.sqlite3"


@pytest.fixture
def engine(db_file: Path) -> Iterator[Engine]:
    eng = make_engine(db_file)
    create_schema(eng)
    yield eng
    eng.dispose()


def add_user(engine: Engine, username: str = "admin1", created_at: datetime | None = None) -> int:
    """Insert an HR Administrator whose login value is ``login_secret_for_tests()``."""
    when = created_at or DEFAULT_NOW
    return insert_user(engine, username.strip(), normalize_username(username), _test_hash(), when)


# --------------------------------------------------------------------- web
@pytest.fixture
def app(engine: Engine, db_file: Path, fixed_clock: FixedClock):  # type: ignore[no-untyped-def]
    from tests.web_helpers import build_app

    return build_app(db_file)


@pytest.fixture
def client(app):  # type: ignore[no-untyped-def]
    return app.test_client()


@pytest.fixture
def admin_id(engine: Engine) -> int:
    return add_user(engine, "admin1")


@pytest.fixture
def logged_in(client, admin_id):  # type: ignore[no-untyped-def]
    """A test client with an authenticated HR Administrator session."""
    from tests.web_helpers import login

    response = login(client, "admin1", login_secret_for_tests())
    assert response.status_code == 303
    return client
