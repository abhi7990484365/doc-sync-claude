"""TASK-012 and TASK-013: aggregate employee validation and password rule."""

from datetime import date

import pytest

from employee_app.validation import FIELD_NAMES, ValidationLimits, validate_employee, validate_password
from employee_app.validation import messages

TODAY = date(2026, 11, 20)
DEPARTMENTS = ("Test Dept A",)


def valid_form() -> dict[str, str]:
    return {
        "first_name": " Test ", "last_name": "Person", "email": " Test.Person@Example.com ",
        "phone": "(555) 123-4567", "department": "Test Dept A", "job_title": "Tester",
        "joining_date": "2026-11-20",
    }


def test_valid_form_returns_cleaned_values_and_normalised_email() -> None:
    outcome = validate_employee(valid_form(), TODAY, DEPARTMENTS)
    assert outcome.is_valid and outcome.errors == {}
    employee = outcome.employee
    assert employee is not None
    assert employee.first_name == "Test"
    assert employee.email == "Test.Person@Example.com"
    assert employee.email_normalized == "test.person@example.com"
    assert employee.phone == "5551234567"
    assert employee.joining_date == date(2026, 11, 20)


def test_all_empty_form_gives_seven_errors() -> None:
    outcome = validate_employee({name: "" for name in FIELD_NAMES}, TODAY, DEPARTMENTS)
    assert set(outcome.errors) == set(FIELD_NAMES)
    assert all(msg == messages.REQUIRED for msg in outcome.errors.values())
    assert outcome.employee is None


def test_missing_keys_are_treated_as_empty_without_raising() -> None:
    outcome = validate_employee({}, TODAY, DEPARTMENTS)
    assert set(outcome.errors) == set(FIELD_NAMES)


def test_several_simultaneous_errors_are_all_reported() -> None:
    form = valid_form() | {"email": "bad", "phone": "123", "joining_date": "2026-01-01", "department": "X"}
    outcome = validate_employee(form, TODAY, DEPARTMENTS)
    assert set(outcome.errors) == {"email", "phone", "joining_date", "department"}


def test_cleaned_values_are_kept_for_redisplay_on_error() -> None:
    outcome = validate_employee(valid_form() | {"email": "  bad  "}, TODAY, DEPARTMENTS)
    assert outcome.cleaned["email"] == "bad" and outcome.cleaned["first_name"] == "Test"


def test_custom_limits_are_applied() -> None:
    form = valid_form() | {"first_name": "abcdefg"}
    outcome = validate_employee(form, TODAY, DEPARTMENTS, ValidationLimits(name_max_length=6))
    assert outcome.errors == {"first_name": messages.TOO_LONG}


def test_non_string_junk_does_not_raise() -> None:
    outcome = validate_employee({"first_name": None, "email": "\x00"}, TODAY, DEPARTMENTS)
    assert "first_name" in outcome.errors and "email" in outcome.errors


# TASK-013 password rule (FR-16, N-17)
@pytest.mark.parametrize("password, error", [("", messages.PASSWORD_EMPTY), ("a" * 11, messages.PASSWORD_TOO_SHORT),
                                             ("a" * 12, None), ("a" * 200, None)])
def test_password_rule(password: str, error: str | None) -> None:
    assert validate_password(password) == error


def test_password_error_never_contains_password() -> None:
    secret = "short-pw-x"
    assert secret not in (validate_password(secret) or "")


def test_password_rule_honours_configured_minimum() -> None:
    assert validate_password("a" * 8, min_length=8) is None
    assert validate_password("a" * 7, min_length=8) == messages.PASSWORD_TOO_SHORT
