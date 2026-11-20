"""TASK-002 smoke tests and TASK-005 clock tests."""

import sys
from datetime import date, datetime, timezone

import employee_app
from employee_app import clock
from tests.helpers import imported_modules


def test_package_imports_on_python_311() -> None:
    assert sys.version_info[:2] == (3, 11)
    assert employee_app.__version__


def test_utc_now_is_timezone_aware_utc() -> None:
    value = clock.utc_now()
    assert value.tzinfo is not None
    assert value.utcoffset().total_seconds() == 0


def test_today_local_returns_a_date() -> None:
    value = clock.today_local()
    assert isinstance(value, date) and not isinstance(value, datetime)


def test_fixed_clock_pins_date_and_time(fixed_clock) -> None:
    assert clock.utc_now() == datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
    assert clock.today_local() == date(2026, 11, 20)


def test_fixed_clock_advance_crosses_date_boundary(fixed_clock) -> None:
    fixed_clock.advance(hours=12)  # E-10 boundary using a fixed instant
    assert clock.today_local() == date(2026, 11, 21)


def test_clock_module_imports_no_flask_or_database() -> None:
    names = " ".join(imported_modules(clock)).lower()
    assert "flask" not in names and "sqlalchemy" not in names
