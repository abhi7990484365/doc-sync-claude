"""Password hashing helpers (Werkzeug scrypt, D-18). Plain text is never stored."""

from functools import cache

from werkzeug.security import check_password_hash, generate_password_hash

HASH_METHOD = "scrypt"


def hash_password(password: str) -> str:
    return generate_password_hash(password, method=HASH_METHOD)


def verify_password(password_hash: str, password: str) -> bool:
    """Constant-structure verification; never raises for a malformed hash."""
    try:
        return check_password_hash(password_hash, password)
    except (ValueError, TypeError):
        return False


@cache
def dummy_hash() -> str:
    """Precomputed hash compared against for unknown users (D-18)."""
    return hash_password("dummy-password-for-unknown-users")
