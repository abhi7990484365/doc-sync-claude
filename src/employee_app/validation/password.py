"""C-4 password rule (FR-16): non-empty and at least the minimum length."""

from employee_app.validation import messages


def validate_password(password: str, min_length: int = 12) -> str | None:
    """Return an error message (never containing the password) or ``None``."""
    if not password:
        return messages.PASSWORD_EMPTY
    if len(password) < min_length:
        return messages.PASSWORD_TOO_SHORT
    return None
