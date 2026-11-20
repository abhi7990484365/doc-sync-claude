"""C-4 username rules (OQ-A11 approved Proposal): trimmed, case-folded, capped."""

from employee_app.validation.text import trim, validate_required_text

USERNAME_MAX_LENGTH = 100


def normalize_username(raw: str | None) -> str:
    """Comparison key: trimmed and case-folded."""
    return trim(raw).casefold()


def validate_username(raw: str | None) -> tuple[str, str | None]:
    """Return ``(trimmed, error)``; required, at most 100 characters."""
    return validate_required_text(raw, USERNAME_MAX_LENGTH)
