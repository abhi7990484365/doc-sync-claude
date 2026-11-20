"""C-2 per-request user loader: one mechanism for every protected route."""

from employee_app import clock
from employee_app.auth.session import SessionUser, session_is_current
from employee_app.db.errors import StorageError
from employee_app.db.users import get_user
from employee_app.extensions import get_state
from employee_app.logging_setup import log_server_error


def load_user(user_id: str) -> SessionUser | None:
    """Return the user, or None (unauthenticated) when the user is missing or
    inactive, the auth_version differs, or the session is too old."""
    state = get_state()
    try:
        view = get_user(state.engine, int(user_id))
    except (StorageError, ValueError) as exc:
        if isinstance(exc, StorageError):
            log_server_error("session_user_read_failed", exc, category=exc.category)
        return None
    if view is None or not view.is_active:
        return None
    if not session_is_current(view, clock.utc_now(), state.settings.session_lifetime_seconds):
        return None
    return SessionUser(view)
