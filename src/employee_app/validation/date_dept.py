"""C-4 department and joining-date rules (FR-7, FR-11).

The current date and the department list are supplied by the caller; this
module never reads the clock or configuration.
"""

import re
from collections.abc import Collection
from datetime import date, timedelta

from employee_app.validation import messages
from employee_app.validation.text import trim

_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def validate_department(raw: str | None, departments: Collection[str]) -> tuple[str, str | None]:
    cleaned = trim(raw)
    if not cleaned:
        return cleaned, messages.REQUIRED
    if cleaned not in departments:
        return cleaned, messages.INVALID_DEPARTMENT
    return cleaned, None


def parse_iso_date(text: str) -> date | None:
    """Strict ``YYYY-MM-DD`` real calendar date, else ``None``."""
    if not _ISO_DATE.fullmatch(text):
        return None
    year, month, day = (int(part) for part in text.split("-"))
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _check_range(value: date, today: date, max_future_days: int | None) -> str | None:
    if value < today:
        return messages.DATE_IN_PAST
    if max_future_days is not None and value > today + timedelta(days=max_future_days):
        return messages.DATE_TOO_FAR
    return None


def validate_joining_date(
    raw: str | None, today: date, max_future_days: int | None = None
) -> tuple[date | None, str | None]:
    cleaned = trim(raw)
    if not cleaned:
        return None, messages.REQUIRED
    parsed = parse_iso_date(cleaned)
    if parsed is None:
        return None, messages.INVALID_DATE
    error = _check_range(parsed, today, max_future_days)
    return (None, error) if error else (parsed, None)
