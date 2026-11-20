"""C-6 employee and audit write plus duplicate pre-check (D-7, D-25)."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine

from employee_app.db.engine import session_scope
from employee_app.db.models import AuditRecord, Employee
from employee_app.validation import ValidatedEmployee


def email_exists(engine: Engine, email_normalized: str) -> bool:
    """Read-only check. Its transaction ends before this function returns, so
    it is never held open into the write (D-25)."""
    with session_scope(engine) as session:
        found = session.execute(
            select(Employee.id).where(Employee.email_normalized == email_normalized)
        ).first()
        return found is not None


def _employee_row(employee: ValidatedEmployee) -> Employee:
    return Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        email_normalized=employee.email_normalized,
        phone=employee.phone,
        department=employee.department,
        job_title=employee.job_title,
        joining_date=employee.joining_date,
    )


def insert_employee_with_audit(
    engine: Engine, employee: ValidatedEmployee, admin_id: int, created_at: datetime
) -> int:
    """Insert Employee and AuditRecord in one write transaction and commit.

    Returns the employee id. Raises IntegrityConflict (rolled back) on a
    constraint failure and StorageError on any other database failure; in every
    failure case neither row remains.
    """
    with session_scope(engine, write=True) as session:
        row = _employee_row(employee)
        session.add(row)
        session.flush()
        session.add(AuditRecord(employee_id=row.id, created_by_user_id=admin_id, created_at=created_at))
        session.commit()
        return row.id
