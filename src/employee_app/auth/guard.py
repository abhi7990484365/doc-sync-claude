"""C-2 ordered access control for protected routes (D-5).

Step 1: authentication, session validity and role (page request: 302 to
login; submission: 401; wrong role: 403). The body is not read.
Step 2: explicit CSRF check for non-safe methods (403).
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from flask import abort, redirect, request, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from employee_app.db.models import ROLE_HR_ADMINISTRATOR
from employee_app.extensions import csrf

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
F = TypeVar("F", bound=Callable[..., Any])


def _login_redirect() -> Response:
    return redirect(url_for("auth.login"))  # type: ignore[return-value]


def check_access() -> Response | None:
    """Return a redirect for an unauthenticated page request; abort for
    everything else that is not allowed; None when the request may proceed."""
    if not current_user.is_authenticated:
        if request.method in SAFE_METHODS:
            return _login_redirect()
        abort(401)
    if current_user.role != ROLE_HR_ADMINISTRATOR:
        abort(403)
    if request.method not in SAFE_METHODS:
        csrf.protect()  # raises CSRFError (403 page) on failure
    return None


def protected(view: F) -> F:
    """Decorator: every protected route goes through ``check_access``."""

    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        denied = check_access()
        if denied is not None:
            return denied
        return view(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
