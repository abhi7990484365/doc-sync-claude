"""TASK-011: department and joining-date rules (N-6, P-5, P-13, E-2, E-11)."""

from datetime import date

import pytest

from employee_app.validation import messages
from tests.helpers import imported_modules
from employee_app.validation.date_dept import parse_iso_date, validate_department, validate_joining_date

TODAY = date(2026, 11, 20)
DEPARTMENTS = ("Test Dept A", "Test Dept B")


def test_yesterday_rejected() -> None:
    assert validate_joining_date("2026-11-19", TODAY) == (None, messages.DATE_IN_PAST)


@pytest.mark.parametrize("raw, expected", [("2026-11-20", date(2026, 11, 20)), ("2026-11-21", date(2026, 11, 21))])
def test_today_and_tomorrow_accepted(raw: str, expected: date) -> None:
    assert validate_joining_date(raw, TODAY) == (expected, None)


def test_far_future_accepted_without_maximum() -> None:
    assert validate_joining_date("2999-12-31", TODAY)[1] is None


def test_optional_maximum_future_days_is_enforced_when_configured() -> None:
    assert validate_joining_date("2026-11-30", TODAY, max_future_days=10)[1] is None
    assert validate_joining_date("2026-12-01", TODAY, max_future_days=10)[1] == messages.DATE_TOO_FAR


@pytest.mark.parametrize(
    "raw", ["2026-02-30", "not a date", "20261120", "2026-1-5", "2026/11/20", "2026-W47-5", "\u0662026-11-20"]
)
def test_unparseable_or_non_iso_dates_rejected(raw: str) -> None:
    assert validate_joining_date(raw, TODAY) == (None, messages.INVALID_DATE)


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_empty_date_is_required(raw: str | None) -> None:
    assert validate_joining_date(raw, TODAY) == (None, messages.REQUIRED)


def test_leap_day_parsing() -> None:
    assert parse_iso_date("2028-02-29") == date(2028, 2, 29)
    assert parse_iso_date("2027-02-29") is None


def test_department_in_list_accepted() -> None:
    assert validate_department(" Test Dept A ", DEPARTMENTS) == ("Test Dept A", None)


def test_department_outside_list_rejected() -> None:
    assert validate_department("Other", DEPARTMENTS)[1] == messages.INVALID_DEPARTMENT


def test_department_empty_and_empty_list() -> None:
    assert validate_department("", DEPARTMENTS)[1] == messages.REQUIRED
    assert validate_department("Test Dept A", ())[1] == messages.INVALID_DEPARTMENT


def test_module_has_no_clock_import() -> None:
    import employee_app.validation.date_dept as module

    names = " ".join(imported_modules(module))
    assert "clock" not in names and "flask" not in names
    assert "datetime.now" not in open(module.__file__, encoding="utf-8").read()
