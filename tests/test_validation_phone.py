"""TASK-010: phone rules (P-3, P-6, N-5)."""

import pytest

from employee_app.validation import messages
from employee_app.validation.phone import validate_phone


@pytest.mark.parametrize(
    "raw, digits",
    [("5551234567", "5551234567"), ("(555) 123-4567", "5551234567"), ("555 123 4567", "5551234567"),
     ("  555-123-4567  ", "5551234567")],
)
def test_valid_phone_stores_ten_digits(raw: str, digits: str) -> None:
    assert validate_phone(raw) == (digits, None)


@pytest.mark.parametrize(
    "raw",
    ["555123456", "55512345678", "555123456a", "+1 555 123 4567", "+5551234567", "555.123.4567",
     "\u0665\u0665\u0665\u0661\u0662\u0663\u0664\u0665\u0666\u0667",  # Arabic-Indic digits
     "555\u2013123\u20134567",  # en dashes
     "555\u2011123\u20114567",  # non-breaking hyphens
     ],
)
def test_invalid_phone_rejected(raw: str) -> None:
    assert validate_phone(raw)[1] == messages.INVALID_PHONE


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_empty_phone_is_required_error(raw: str | None) -> None:
    assert validate_phone(raw)[1] == messages.REQUIRED
