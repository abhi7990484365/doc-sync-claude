"""C-11 Logging: one-line events that can only carry ids and categories.

Redaction is by construction: ``log_event`` accepts only allow-listed field
names whose values are integers or short category tokens. Passwords, hashes,
cookies, CSRF tokens, the signing key, attempted usernames and employee
personal data have no field to travel in.
"""

import logging
import re

ALLOWED_FIELDS = frozenset(
    {"user_id", "employee_id", "admin_id", "category", "command", "outcome", "count", "duration_ms", "status"}
)
_TOKEN = re.compile(r"[A-Za-z0-9_.:-]{1,64}")
LOGGER_NAME = "employee_app"


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(level: int = logging.INFO) -> None:
    """Install a single stream handler on the application logger (idempotent)."""
    logger = get_logger()
    logger.setLevel(level)
    if not any(getattr(h, "_employee_app", False) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        handler._employee_app = True  # type: ignore[attr-defined]
        logger.addHandler(handler)


def _format_value(name: str, value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"log field {name} must be an int or a token")
    text = str(value)
    if not _TOKEN.fullmatch(text):
        raise ValueError(f"log field {name} is not a safe token")
    return text


def format_event(event: str, **fields: int | str) -> str:
    """Build the one-line message; raises ValueError for any unsafe field."""
    if not _TOKEN.fullmatch(event):
        raise ValueError("event name is not a safe token")
    parts = [event]
    for name, value in fields.items():
        if name not in ALLOWED_FIELDS:
            raise ValueError(f"log field {name} is not allowed")
        parts.append(f"{name}={_format_value(name, value)}")
    return " ".join(parts)


def log_event(level: int, event: str, **fields: int | str) -> None:
    get_logger().log(level, format_event(event, **fields))


def log_server_error(event: str, exc: BaseException, **fields: int | str) -> None:
    """Server-side only: message is safe; the traceback goes to the log file/stream.

    The exception text is not placed in the message. The traceback is attached
    through ``exc_info`` (storage exceptions hide statement parameters, D-21).
    """
    get_logger().error(format_event(event, **fields), exc_info=exc)
