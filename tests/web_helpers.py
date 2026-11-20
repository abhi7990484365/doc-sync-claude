"""Helpers for Flask test-client tests. CSRF protection stays enabled."""

import re
from datetime import date
from pathlib import Path
from typing import Any

from flask import Flask
from flask.testing import FlaskClient

from employee_app.app import create_app
from employee_app.config import CoreSettings, DatabaseSettings, WebSettings

TEST_DEPARTMENTS = ("Test Dept A", "Test Dept B")  # labelled test data; real names are Not Found
FAKE_SIGNING_KEY = "unit-test-signing-key-not-a-secret"
TOKEN_RE = re.compile(r'name="csrf_token" value="([^"]+)"')


def web_settings(db_file: Path, **overrides: Any) -> WebSettings:
    values: dict[str, Any] = {
        "core": CoreSettings(database=DatabaseSettings(str(db_file), 2.0)),
        "secret_key": FAKE_SIGNING_KEY,
        "cookie_secure": False,
        "mode": "testing",
        "departments": TEST_DEPARTMENTS,
    }
    values.update(overrides)
    return WebSettings(**values)


def build_app(db_file: Path, **overrides: Any) -> Flask:
    return create_app(web_settings(db_file, **overrides))


def csrf_token(html: str) -> str:
    match = TOKEN_RE.search(html)
    assert match, "no CSRF token on the page"
    return match.group(1)


def strip_tokens(html: str) -> str:
    """Remove CSRF token values so page bodies can be compared."""
    return TOKEN_RE.sub('name="csrf_token" value="X"', html)


def valid_form(**overrides: str) -> dict[str, str]:
    """A valid form dictionary; each case overrides one field."""
    form = {
        "first_name": "Test", "last_name": "Person", "email": "test.person@example.com",
        "phone": "(555) 123-4567", "department": TEST_DEPARTMENTS[0], "job_title": "Tester",
        "joining_date": date(2026, 11, 20).isoformat(),
    }
    form.update(overrides)
    return form


def page_token(client: FlaskClient, path: str = "/login") -> str:
    return csrf_token(client.get(path).get_data(as_text=True))


def login(client: FlaskClient, username: str, secret: str):  # type: ignore[no-untyped-def]
    token = page_token(client, "/login")
    return client.post("/login", data={"csrf_token": token, "username": username, "password": secret})


def post_employee(client: FlaskClient, form: dict[str, str], token: str | None = None):  # type: ignore[no-untyped-def]
    token = token if token is not None else page_token(client, "/employees/new")
    return client.post("/employees/new", data={**form, "csrf_token": token})


def employee_counts(engine) -> tuple[int, int]:  # type: ignore[no-untyped-def]
    """(employee rows, audit rows)."""
    from sqlalchemy import func, select

    from employee_app.db.engine import session_scope
    from employee_app.db.models import AuditRecord, Employee

    with session_scope(engine) as s:
        return (s.scalar(select(func.count()).select_from(Employee)),
                s.scalar(select(func.count()).select_from(AuditRecord)))


def set_role(engine, user_id: int, role: str) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import update

    from employee_app.db.models import User
    from employee_app.db.statements import execute_write

    execute_write(engine, update(User).where(User.id == user_id).values(role=role))
