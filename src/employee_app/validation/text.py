"""C-4 trim helper and text-field rules (no Flask, no database)."""

from employee_app.validation import messages


def trim(value: str | None) -> str:
    """Unicode-aware strip. ``None`` counts as an empty value."""
    return (value or "").strip()


def validate_required_text(raw: str | None, max_length: int) -> tuple[str, str | None]:
    """Return ``(cleaned, error)`` for a required free-text field.

    Length is counted in code points after trimming. Allowed characters are
    Not Found in requirements, so none are restricted.
    """
    cleaned = trim(raw)
    if not cleaned:
        return cleaned, messages.REQUIRED
    if len(cleaned) > max_length:
        return cleaned, messages.TOO_LONG
    return cleaned, None
