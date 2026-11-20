"""C-4 phone rules (FR-6, D-13)."""

from employee_app.validation import messages
from employee_app.validation.text import trim

_STRIPPED = " -()"
_ASCII_DIGITS = frozenset("0123456789")
PHONE_DIGITS = 10


def validate_phone(raw: str | None) -> tuple[str, str | None]:
    """Return ``(value, error)``; on success value is the 10 ASCII digits."""
    cleaned = trim(raw)
    if not cleaned:
        return cleaned, messages.REQUIRED
    if "+" in cleaned:
        return cleaned, messages.INVALID_PHONE
    digits = "".join(ch for ch in cleaned if ch not in _STRIPPED)
    if len(digits) != PHONE_DIGITS or not set(digits) <= _ASCII_DIGITS:
        return cleaned, messages.INVALID_PHONE
    return digits, None
