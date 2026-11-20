"""C-4 email rules and normalisation (FR-4, FR-5)."""

from employee_app.validation import messages
from employee_app.validation.text import trim


def _is_basic_email(value: str) -> bool:
    if any(ch.isspace() for ch in value) or value.count("@") != 1:
        return False
    local, domain = value.split("@")
    labels = domain.split(".")
    return bool(local) and len(labels) >= 2 and all(labels)


def normalize_email(cleaned_email: str) -> str:
    """Case-insensitive comparison key (D-3): trimmed value through casefold()."""
    return trim(cleaned_email).casefold()


def validate_email(raw: str | None, max_length: int) -> tuple[str, str | None]:
    """Return ``(cleaned, error)``."""
    cleaned = trim(raw)
    if not cleaned:
        return cleaned, messages.REQUIRED
    if len(cleaned) > max_length:
        return cleaned, messages.TOO_LONG
    if not _is_basic_email(cleaned):
        return cleaned, messages.INVALID_EMAIL
    return cleaned, None
