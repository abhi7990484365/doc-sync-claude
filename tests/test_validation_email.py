"""TASK-009: email rules and normalisation (N-3, E-4, FR-4, FR-5)."""

import pytest

from employee_app.validation import messages
from employee_app.validation.email import normalize_email, validate_email


@pytest.mark.parametrize("value", ["a@b.co", "jane.doe@example.com", "a+tag@sub.example.org"])
def test_valid_emails(value: str) -> None:
    assert validate_email(value, 254) == (value, None)


@pytest.mark.parametrize(
    "value",
    ["plain", "no-at.example.com", "@example.com", "a@", "a@example", "a@.com", "a@example.", "a@@b.com",
     "a@b@c.com", "a b@example.com", "a@exa mple.com", "a@b..com"],
)
def test_invalid_emails_rejected(value: str) -> None:
    assert validate_email(value, 254)[1] == messages.INVALID_EMAIL


def test_leading_and_trailing_whitespace_is_trimmed() -> None:
    assert validate_email("  a@b.co \t", 254) == ("a@b.co", None)


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_empty_email_is_required_error(raw: str | None) -> None:
    assert validate_email(raw, 254)[1] == messages.REQUIRED


def test_254_characters_accepted_and_255_rejected() -> None:
    local = "a" * (254 - len("@b.co"))
    assert validate_email(local + "@b.co", 254)[1] is None
    assert validate_email("a" + local + "@b.co", 254)[1] == messages.TOO_LONG


def test_case_pair_normalises_equal() -> None:
    assert normalize_email("Jane.Doe@Example.com") == normalize_email("jane.doe@example.com")


def test_non_ascii_case_pair_normalises_equal() -> None:
    assert normalize_email("ÄÖ@Example.de") == normalize_email("äö@example.de")
    assert normalize_email("Straße@example.de") == normalize_email("STRASSE@example.de")


def test_normalize_trims_first() -> None:
    assert normalize_email("  A@B.co ") == "a@b.co"
