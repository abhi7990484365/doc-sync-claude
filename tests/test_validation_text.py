"""TASK-008: trim and text-field rules (N-1, N-2, E-6, E-7, N-18, P-12)."""

import pytest

from employee_app.validation import messages
from tests.helpers import imported_modules
from employee_app.validation.text import trim, validate_required_text


@pytest.mark.parametrize(
    "raw, expected",
    [("  Ann  ", "Ann"), ("\u00a0Ann\u2003", "Ann"), ("", ""), (None, ""), ("   \t\n", "")],
)
def test_trim_is_unicode_aware(raw: str | None, expected: str) -> None:
    assert trim(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", None, "\u2003\t"])
def test_empty_or_whitespace_only_is_required_error(raw: str | None) -> None:
    assert validate_required_text(raw, 100)[1] == messages.REQUIRED


@pytest.mark.parametrize("length", [1, 100])
def test_boundary_lengths_accepted(length: int) -> None:
    value = "a" * length
    assert validate_required_text(value, 100) == (value, None)


def test_101_characters_rejected() -> None:
    assert validate_required_text("a" * 101, 100)[1] == messages.TOO_LONG


def test_length_counted_after_trim() -> None:
    assert validate_required_text("  " + "a" * 100 + "  ", 100)[1] is None


def test_length_counted_in_code_points_not_bytes() -> None:
    assert validate_required_text("é" * 100, 100)[1] is None
    assert validate_required_text("é" * 101, 100)[1] == messages.TOO_LONG


def test_accented_and_unrestricted_characters_accepted() -> None:
    assert validate_required_text("Zoë O'Brien-Müller 3rd", 100)[1] is None


def test_module_does_not_import_flask_or_database() -> None:
    import employee_app.validation.text as module

    names = " ".join(imported_modules(module)).lower()
    assert "flask" not in names and "sqlalchemy" not in names
