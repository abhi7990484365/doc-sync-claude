"""TASK-017: employee and audit write plus duplicate pre-check."""

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import event, func, select

from employee_app.db.employees import email_exists, insert_employee_with_audit
from employee_app.db.engine import session_scope
from employee_app.db.errors import IntegrityConflict, StorageError
from employee_app.db.models import AuditRecord, Employee
from employee_app.validation import ValidatedEmployee
from tests.conftest import add_user

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


def sample(email: str = "Test.Person@Example.com") -> ValidatedEmployee:
    return ValidatedEmployee("Test", "Person", email, email.casefold(), "5551234567", "Test Dept", "Tester",
                             date(2026, 11, 20))


def counts(engine) -> tuple[int, int]:  # type: ignore[no-untyped-def]
    with session_scope(engine) as s:
        return (s.scalar(select(func.count()).select_from(Employee)),
                s.scalar(select(func.count()).select_from(AuditRecord)))


def test_successful_write_creates_one_employee_and_one_audit_row(engine) -> None:
    admin = add_user(engine)
    employee_id = insert_employee_with_audit(engine, sample(), admin, NOW)
    assert counts(engine) == (1, 1)
    with session_scope(engine) as s:
        audit = s.scalars(select(AuditRecord)).one()
        assert (audit.employee_id, audit.created_by_user_id, audit.created_at) == (employee_id, admin, NOW)


def test_precheck_true_and_false(engine) -> None:
    admin = add_user(engine)
    assert email_exists(engine, "test.person@example.com") is False
    insert_employee_with_audit(engine, sample(), admin, NOW)
    assert email_exists(engine, "test.person@example.com") is True
    assert email_exists(engine, "other@example.com") is False


def test_duplicate_email_raises_conflict_and_rolls_back_both_rows(engine) -> None:
    admin = add_user(engine)
    insert_employee_with_audit(engine, sample(), admin, NOW)
    with pytest.raises(IntegrityConflict):
        insert_employee_with_audit(engine, sample("TEST.PERSON@EXAMPLE.COM"), admin, NOW)
    assert counts(engine) == (1, 1)


def test_audit_insert_failure_leaves_no_employee(engine) -> None:
    admin = add_user(engine)

    def boom(*_args: object) -> None:
        raise RuntimeError("injected audit failure")

    event.listen(AuditRecord, "before_insert", boom)
    try:
        with pytest.raises(RuntimeError):
            insert_employee_with_audit(engine, sample(), admin, NOW)
    finally:
        event.remove(AuditRecord, "before_insert", boom)
    assert counts(engine) == (0, 0)


def test_unknown_admin_id_violates_foreign_key_and_leaves_nothing(engine) -> None:
    with pytest.raises(StorageError):
        insert_employee_with_audit(engine, sample(), 9999, NOW)
    assert counts(engine) == (0, 0)


def test_read_transaction_is_closed_before_the_write_starts(engine, db_file) -> None:
    """The pre-check must not hold a transaction: another connection can write
    immediately afterwards with a very short busy wait."""
    from tests.conftest import make_engine

    admin = add_user(engine)
    email_exists(engine, "x@y.co")
    writer = make_engine(db_file, busy=0.05)
    insert_employee_with_audit(writer, sample(), admin, NOW)
    assert counts(engine) == (1, 1)
    writer.dispose()
