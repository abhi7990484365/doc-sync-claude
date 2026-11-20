"""C-4 aggregate validation of the seven employee fields (FR-2, FR-3, FR-10)."""

from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from employee_app.validation.date_dept import validate_department, validate_joining_date
from employee_app.validation.email import normalize_email, validate_email
from employee_app.validation.limits import ValidationLimits
from employee_app.validation.phone import validate_phone
from employee_app.validation.text import validate_required_text

FIELD_NAMES = ("first_name", "last_name", "email", "phone", "department", "job_title", "joining_date")


@dataclass(frozen=True)
class ValidatedEmployee:
    first_name: str
    last_name: str
    email: str
    email_normalized: str
    phone: str
    department: str
    job_title: str
    joining_date: date


@dataclass(frozen=True)
class ValidationOutcome:
    employee: ValidatedEmployee | None = None
    errors: dict[str, str] = field(default_factory=dict)
    cleaned: dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _run_rules(
    raw: Mapping[str, str | None], today: date, departments: Collection[str], limits: ValidationLimits
) -> dict[str, tuple[Any, str | None]]:
    return {
        "first_name": validate_required_text(raw.get("first_name"), limits.name_max_length),
        "last_name": validate_required_text(raw.get("last_name"), limits.name_max_length),
        "email": validate_email(raw.get("email"), limits.email_max_length),
        "phone": validate_phone(raw.get("phone")),
        "department": validate_department(raw.get("department"), departments),
        "job_title": validate_required_text(raw.get("job_title"), limits.name_max_length),
        "joining_date": validate_joining_date(raw.get("joining_date"), today, limits.max_future_days),
    }


def _display_value(value: Any) -> str:
    return value.isoformat() if isinstance(value, date) else str(value or "")


def _build_employee(values: dict[str, Any]) -> ValidatedEmployee:
    return ValidatedEmployee(
        first_name=values["first_name"],
        last_name=values["last_name"],
        email=values["email"],
        email_normalized=normalize_email(values["email"]),
        phone=values["phone"],
        department=values["department"],
        job_title=values["job_title"],
        joining_date=values["joining_date"],
    )


def validate_employee(
    raw: Mapping[str, str | None],
    today: date,
    departments: Collection[str],
    limits: ValidationLimits | None = None,
) -> ValidationOutcome:
    """Validate all fields, collecting every error. Never raises for user input."""
    results = _run_rules(raw, today, departments, limits or ValidationLimits())
    errors = {name: err for name, (_, err) in results.items() if err}
    cleaned = {name: _display_value(value) for name, (value, _) in results.items()}
    if errors:
        return ValidationOutcome(errors=errors, cleaned=cleaned)
    values = {name: value for name, (value, _) in results.items()}
    return ValidationOutcome(employee=_build_employee(values), cleaned=cleaned)
