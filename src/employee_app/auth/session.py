"""C-2 session issue and validation (D-16).

The signed cookie carries the user id (Flask-Login), the ``auth_version`` at
login and the issue time. Revocation works through ``auth_version``; the
maximum lifetime is enforced on the server with the C-8 clock.
"""

from datetime import datetime

from flask import session
from flask_login import UserMixin, login_user, logout_user

from employee_app.db.users import UserView

KEY_AUTH_VERSION = "auth_version"
KEY_ISSUED_AT = "issued_at"


class SessionUser(UserMixin):  # type: ignore[misc]
    """Flask-Login user wrapper around a plain ``UserView``."""

    def __init__(self, view: UserView) -> None:
        self.view = view
        self.role = view.role

    def get_id(self) -> str:
        return str(self.view.id)

    @property
    def is_active(self) -> bool:  # type: ignore[override]
        return self.view.is_active


def start_session(user: UserView, now: datetime) -> None:
    """Clear the old session and issue a fresh one (no remember-me)."""
    session.clear()
    login_user(SessionUser(user), remember=False)
    session[KEY_AUTH_VERSION] = user.auth_version
    session[KEY_ISSUED_AT] = int(now.timestamp())
    session.permanent = True


def end_session() -> None:
    logout_user()
    session.clear()


def session_is_current(view: UserView, now: datetime, max_lifetime_seconds: int) -> bool:
    """True if the session's version matches and it is not older than the maximum."""
    issued = session.get(KEY_ISSUED_AT)
    if not isinstance(issued, int) or session.get(KEY_AUTH_VERSION) != view.auth_version:
        return False
    return 0 <= now.timestamp() - issued <= max_lifetime_seconds
