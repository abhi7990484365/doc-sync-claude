"""C-5 Employee service: the create-employee use case (FR-5, FR-8, FR-13, FR-17).

Order: validate (C-4) -> duplicate pre-check (a read that ends before the write)
-> one write transaction (employee + audit) -> on an integrity error re-query
``email_normalized`` to choose the email-in-use error or a generic failure.
"""

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.engine import Engine

from employee_app import clock
from employee_app.config import WebSettings
from employee_app.db.employees import email_exists, insert_employee_with_audit
from employee_app.db.errors import IntegrityConflict, StorageError
from employee_app.logging_setup import log_event, log_server_error
from employee_app.validation import ValidatedEmployee, validate_employee
from employee_app.validation.messages import EMAIL_IN_USE


class CreateStatus(Enum):
    CREATED = "created"
    INVALID = "invalid"
    FAILED = "failed"


@dataclass(frozen=True)
class CreateResult:
    status: CreateStatus
    errors: dict[str, str] = field(default_factory=dict)
    values: dict[str, str] = field(default_factory=dict)
    employee_id: int | None = None


def _pre_check(engine: Engine, email_normalized: str) -> bool:
    """Duplicate pre-check (friendly message in the normal case)."""
    return email_exists(engine, email_normalized)


def _invalid(errors: dict[str, str], values: dict[str, str]) -> CreateResult:
    return CreateResult(CreateStatus.INVALID, errors=errors, values=values)


def _failed(values: dict[str, str], exc: StorageError) -> CreateResult:
    log_server_error("employee_create_failed", exc, category=exc.category)
    return CreateResult(CreateStatus.FAILED, values=values)


def _write(
    engine: Engine, employee: ValidatedEmployee, admin_id: int, values: dict[str, str]
) -> CreateResult:
    try:
        employee_id = insert_employee_with_audit(engine, employee, admin_id, clock.utc_now())
    except IntegrityConflict as conflict:
        return _after_conflict(engine, employee, values, conflict)
    except StorageError as exc:
        return _failed(values, exc)
    log_event(logging.INFO, "employee_created", employee_id=employee_id, admin_id=admin_id)
    return CreateResult(CreateStatus.CREATED, employee_id=employee_id)


def _after_conflict(
    engine: Engine, employee: ValidatedEmployee, values: dict[str, str], conflict: IntegrityConflict
) -> CreateResult:
    """Integrity error: duplicate email if the key now exists, else generic."""
    try:
        duplicate = email_exists(engine, employee.email_normalized)
    except StorageError as exc:
        return _failed(values, exc)
    if duplicate:
        log_event(logging.INFO, "duplicate_rejected", category="race")
        return _invalid({"email": EMAIL_IN_USE}, values)
    return _failed(values, conflict)


def create_employee(
    engine: Engine, settings: WebSettings, raw: Mapping[str, str | None], admin_id: int
) -> CreateResult:
    outcome = validate_employee(raw, clock.today_local(), settings.departments, settings.core.limits)
    if not outcome.is_valid:
        log_event(logging.INFO, "validation_failed", count=len(outcome.errors))
        return _invalid(outcome.errors, outcome.cleaned)
    employee = outcome.employee
    assert employee is not None
    try:
        duplicate = _pre_check(engine, employee.email_normalized)
    except StorageError as exc:
        return _failed(outcome.cleaned, exc)
    if duplicate:
        log_event(logging.INFO, "duplicate_rejected", category="pre_check")
        return _invalid({"email": EMAIL_IN_USE}, outcome.cleaned)
    return _write(engine, employee, admin_id, outcome.cleaned)
