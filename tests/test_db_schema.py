"""TASK-014 persistence schema and session lifecycle; TASK-015 verification."""

from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from employee_app.db import create_schema
from employee_app.db.engine import check_reachable, session_scope
from employee_app.db.errors import SchemaVerificationError, StorageError
from employee_app.db.models import AuditRecord, Employee, User
from employee_app.db.verify import find_schema_problems, verify_schema
from tests.conftest import add_user, make_engine

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


def employee_row(email_normalized: str = "a@b.co") -> Employee:
    return Employee(first_name="T", last_name="P", email=email_normalized, email_normalized=email_normalized,
                    phone="5551234567", department="D", job_title="J", joining_date=date(2026, 11, 20))


def test_schema_creation_on_temporary_file_database(engine) -> None:
    assert find_schema_problems(engine) == []
    verify_schema(engine)


def test_create_schema_is_repeatable(engine) -> None:
    create_schema(engine)
    verify_schema(engine)


def test_foreign_keys_and_wal_are_on(engine) -> None:
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
        assert conn.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"


def test_duplicate_username_normalized_rejected(engine) -> None:
    add_user(engine, "Admin1")
    with pytest.raises(StorageError) as caught:
        add_user(engine, "ADMIN1")
    assert caught.value.category == "IntegrityError"


def test_duplicate_email_normalized_rejected(engine) -> None:
    with session_scope(engine, write=True) as s:
        s.add(employee_row())
        s.commit()
    with pytest.raises(StorageError):
        with session_scope(engine, write=True) as s:
            s.add(employee_row())
            s.commit()


def test_foreign_key_enforced_for_audit_record(engine) -> None:
    with pytest.raises(StorageError):
        with session_scope(engine, write=True) as s:
            s.add(AuditRecord(employee_id=999, created_by_user_id=999, created_at=NOW))
            s.commit()


def test_only_one_audit_row_per_employee(engine) -> None:
    admin = add_user(engine)
    with session_scope(engine, write=True) as s:
        emp = employee_row()
        s.add(emp)
        s.flush()
        s.add(AuditRecord(employee_id=emp.id, created_by_user_id=admin, created_at=NOW))
        s.commit()
        employee_id = emp.id
    with pytest.raises(StorageError):
        with session_scope(engine, write=True) as s:
            s.add(AuditRecord(employee_id=employee_id, created_by_user_id=admin, created_at=NOW))
            s.commit()


def test_session_closed_and_uncommitted_work_rolled_back(engine) -> None:
    with session_scope(engine, write=True) as s:
        s.add(employee_row("x@y.co"))
        s.flush()
        captured = s
    with Session(engine) as check:
        assert check.query(Employee).count() == 0
    assert captured.in_transaction() is False


def test_session_closed_after_error(engine) -> None:
    with pytest.raises(RuntimeError):
        with session_scope(engine) as s:
            captured = s
            raise RuntimeError("boom")
    assert captured.in_transaction() is False


def test_utc_datetimes_round_trip_aware(engine) -> None:
    add_user(engine)
    with session_scope(engine) as s:
        created = s.query(User).one().created_at
    assert created == NOW and created.tzinfo is not None


def test_naive_datetime_is_refused(engine) -> None:
    with pytest.raises(StorageError):  # SQLAlchemy wraps the ValueError
        add_user(engine, created_at=datetime(2026, 1, 1))


def test_no_update_or_delete_api_for_employees_or_audit() -> None:
    import employee_app.db.employees as module

    public = [n for n in dir(module) if not n.startswith("_")]
    assert not [n for n in public if "delete" in n.lower() or "update" in n.lower()]


# ------------------------------------------------------------- TASK-015
def test_verify_fails_on_empty_database(db_file: Path) -> None:
    eng = make_engine(db_file)
    with pytest.raises(SchemaVerificationError) as caught:
        verify_schema(eng)
    message = str(caught.value)
    assert "'user'" in message and "'employee'" in message and "'audit_record'" in message


def test_verify_fails_for_missing_table(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE audit_record"))
    with pytest.raises(SchemaVerificationError, match="audit_record"):
        verify_schema(engine)


@pytest.mark.parametrize(
    ("index", "expected"),
    [("ux_employee_email_normalized", "employee.email_normalized"),
     ("ux_user_username_normalized", "user.username_normalized"),
     ("ux_audit_record_employee_id", "audit_record.employee_id")],
)
def test_verify_fails_for_missing_unique_index(engine, index: str, expected: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"DROP INDEX {index}"))
    with pytest.raises(SchemaVerificationError, match=expected.replace(".", r"\.")):
        verify_schema(engine)


def test_verify_fails_for_non_unique_index(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP INDEX ux_employee_email_normalized"))
        conn.execute(text("CREATE INDEX ix_plain ON employee (email_normalized)"))
    with pytest.raises(SchemaVerificationError, match=r"employee\.email_normalized"):
        verify_schema(engine)


def test_unreachable_database_is_a_storage_error(tmp_path: Path) -> None:
    eng = make_engine(tmp_path / "missing-dir" / "x.sqlite3")
    with pytest.raises(StorageError):
        check_reachable(eng)
    with pytest.raises(StorageError):
        verify_schema(eng)
