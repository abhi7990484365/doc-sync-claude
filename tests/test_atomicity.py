"""TASK-036: atomicity and graceful storage failure (E-14, N-9, NFR-4)."""

import pytest
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from employee_app.config import CoreSettings, DatabaseSettings
from employee_app.db.engine import write_engine
from employee_app.db.models import AuditRecord
from tests.conftest import make_engine
from tests.web_helpers import build_app, employee_counts, login, post_employee, valid_form
from tests.conftest import login_secret_for_tests

FORBIDDEN = ("Traceback", "OperationalError", "sqlite", "SELECT", "INSERT", "disk full", "File \"")


def assert_generic_500(response) -> None:  # type: ignore[no-untyped-def]
    body = response.get_data(as_text=True)
    assert response.status_code == 500
    assert "Something went wrong" in body and 'href="/login"' in body
    assert not [word for word in FORBIDDEN if word in body]


def test_audit_insert_failure_leaves_no_employee(logged_in, engine) -> None:
    def fail(*_a: object) -> None:
        raise OperationalError("INSERT INTO audit_record", {}, Exception("disk full"))

    event.listen(AuditRecord, "before_insert", fail)
    try:
        response = post_employee(logged_in, valid_form())
    finally:
        event.remove(AuditRecord, "before_insert", fail)
    assert_generic_500(response)
    assert employee_counts(engine) == (0, 0)


def test_commit_failure_leaves_no_employee_and_no_audit_row(logged_in, engine) -> None:
    def fail(_session: Session) -> None:
        raise OperationalError("COMMIT", {}, Exception("disk full"))

    event.listen(Session, "before_commit", fail)
    try:
        response = post_employee(logged_in, valid_form())
    finally:
        event.remove(Session, "before_commit", fail)
    assert_generic_500(response)
    assert employee_counts(engine) == (0, 0)


def test_system_recovers_after_a_failed_write(logged_in, engine) -> None:
    def fail(*_a: object) -> None:
        raise OperationalError("INSERT", {}, Exception("disk full"))

    event.listen(AuditRecord, "before_insert", fail)
    try:
        post_employee(logged_in, valid_form())
    finally:
        event.remove(AuditRecord, "before_insert", fail)
    assert post_employee(logged_in, valid_form()).status_code == 303
    assert employee_counts(engine) == (1, 1)


def test_failed_busy_wait_gives_the_generic_page(engine, db_file, admin_id, fixed_clock) -> None:
    short = CoreSettings(database=DatabaseSettings(str(db_file), 0.2))
    client = build_app(db_file, core=short).test_client()
    assert login(client, "admin1", login_secret_for_tests()).status_code == 303
    holder = make_engine(db_file)
    with write_engine(holder).connect() as conn:
        conn.begin()  # another writer holds the write lock
        response = post_employee(client, valid_form())
        conn.rollback()
    assert_generic_500(response)
    assert employee_counts(engine) == (0, 0)


def test_storage_unavailable_on_the_precheck_read_gives_the_generic_page(logged_in, engine, monkeypatch) -> None:
    def broken(*_a: object) -> bool:
        raise OperationalError("SELECT", {}, Exception("unable to open database file"))

    monkeypatch.setattr("employee_app.db.employees.session_scope", broken)
    response = post_employee(logged_in, valid_form())
    assert response.status_code == 500 and "unable to open" not in response.get_data(as_text=True)
    assert employee_counts(engine) == (0, 0)


@pytest.mark.parametrize("target", ["flush", "commit"])
def test_session_level_failures_roll_back(engine, admin_id, target) -> None:
    from datetime import datetime, timezone

    from employee_app.db.employees import insert_employee_with_audit
    from employee_app.db.errors import StorageError
    from tests.test_db_employee_write import sample

    def fail(*_a: object) -> None:
        raise OperationalError(target, {}, Exception("x"))

    hook = "after_flush" if target == "flush" else "before_commit"
    event.listen(Session, hook, fail)
    try:
        with pytest.raises(StorageError):
            insert_employee_with_audit(engine, sample(), admin_id, datetime(2026, 11, 20, tzinfo=timezone.utc))
    finally:
        event.remove(Session, hook, fail)
    assert employee_counts(engine) == (0, 0)
