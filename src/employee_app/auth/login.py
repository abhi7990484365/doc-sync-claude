"""C-2 login with lockout (3.2, 6.3, D-15, D-18, NR-12).

Every failure cause ends in the same ``None`` result, so the caller can show
one generic message with one status. Nothing logged here contains a username.
"""

import logging
from datetime import datetime

from employee_app import clock
from employee_app.config import LockoutSettings
from employee_app.db.errors import StorageError
from employee_app.db.lockout import record_failure, record_success
from employee_app.db.users import UserView, find_user_by_username
from employee_app.extensions import AppState
from employee_app.logging_setup import log_event, log_server_error
from employee_app.security import dummy_hash, verify_password
from employee_app.validation.username import normalize_username


def _reject(category: str, user_id: int | None = None) -> UserView | None:
    """Log the reason category (never a username) and return None."""
    fields: dict[str, int | str] = {"category": category}
    if user_id is not None:
        fields["user_id"] = user_id
    log_event(logging.INFO, "login_failure", **fields)
    return None


def _fail_closed(exc: StorageError, user_id: int | None) -> None:
    fields: dict[str, int | str] = {"category": exc.category}
    if user_id is not None:
        fields["user_id"] = user_id
    log_server_error("login_storage_error", exc, **fields)


def _lock_will_be_set(user: UserView, now: datetime, settings: LockoutSettings) -> bool:
    expired = user.locked_until is not None and user.locked_until <= now
    next_count = 1 if expired else user.failed_login_count + 1
    return next_count >= settings.max_failures


def _count_failure(state: AppState, user: UserView, now: datetime) -> None:
    """Counter write on the failure path; a failed write is logged, not raised."""
    lockout = state.settings.core.lockout
    try:
        changed = record_failure(state.engine, user.id, now, lockout)
    except StorageError as exc:
        _fail_closed(exc, user.id)
        return
    if changed and _lock_will_be_set(user, now, lockout):
        log_event(logging.WARNING, "account_locked", user_id=user.id)


def _confirm_success(state: AppState, user: UserView, now: datetime) -> bool:
    """Conditional success reset; False means the login must be rejected."""
    try:
        return record_success(state.engine, user.id, now)
    except StorageError as exc:
        _fail_closed(exc, user.id)
        return False


def _find_user(state: AppState, normalized: str) -> UserView | None:
    if not normalized:
        return None
    try:
        return find_user_by_username(state.engine, normalized)
    except StorageError as exc:
        _fail_closed(exc, None)
        return None


def attempt_login(state: AppState, raw_username: str, password: str) -> UserView | None:
    """Return the authenticated user or None for any failure cause."""
    now = clock.utc_now()
    user = _find_user(state, normalize_username(raw_username))
    # Always verify a hash: the real one, or a dummy for unknown users (D-18).
    password_ok = verify_password(user.password_hash if user else dummy_hash(), password)
    if user is None:
        return _reject("unknown_user")
    if not user.is_active:
        return _reject("inactive", user.id)
    if user.is_locked(now):  # NR-12: no lockout write while a lock is active
        return _reject("locked", user.id)
    if not password_ok:
        _count_failure(state, user, now)
        return _reject("bad_password", user.id)
    if not _confirm_success(state, user, now):
        return _reject("success_reset_failed", user.id)
    log_event(logging.INFO, "login_success", user_id=user.id)
    return user

