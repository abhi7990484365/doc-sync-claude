"""C-6 lockout, unlock: single conditional statements (D-15, FR-16, FR-18).

Each function commits in its own short transaction that begins as a write.
Time is passed in (UTC); nothing here reads the clock.
"""

from datetime import datetime, timedelta

from sqlalchemy import and_, case, literal, null, or_, update
from sqlalchemy.engine import Engine

from employee_app.config import LockoutSettings
from employee_app.db.models import User, UTCDateTime
from employee_app.db.statements import execute_write


def _lock_expired(now: datetime) -> object:
    return and_(User.locked_until.is_not(None), User.locked_until <= now)


def _not_locked(now: datetime) -> object:
    return or_(User.locked_until.is_(None), User.locked_until <= now)


def record_failure(engine: Engine, user_id: int, now: datetime, settings: LockoutSettings) -> bool:
    """Count one failed login for an active, not currently locked account.

    One UPDATE: restarts the count at 1 when the previous lock expired,
    otherwise increments; sets ``locked_until`` when the new count reaches the
    limit. Changes nothing while locked or inactive. Returns True if a row
    changed.
    """
    new_count = case((_lock_expired(now), 1), else_=User.failed_login_count + 1)
    lock_until = literal(now + timedelta(minutes=settings.lock_minutes), UTCDateTime)
    statement = (
        update(User)
        .where(User.id == user_id, User.is_active.is_(True), _not_locked(now))
        .values(
            failed_login_count=new_count,
            locked_until=case((new_count >= settings.max_failures, lock_until), else_=null()),
        )
    )
    return execute_write(engine, statement) > 0


def record_success(engine: Engine, user_id: int, now: datetime) -> bool:
    """Reset count and clear the lock only if not locked at this moment.

    Returns False when no row changed (a lock exists), so the caller must
    reject the login.
    """
    statement = (
        update(User)
        .where(User.id == user_id, _not_locked(now))
        .values(failed_login_count=0, locked_until=None)
    )
    return execute_write(engine, statement) > 0


def unlock(engine: Engine, user_id: int) -> bool:
    """Clear count and lock in one update. Touches nothing else. Idempotent."""
    statement = update(User).where(User.id == user_id).values(failed_login_count=0, locked_until=None)
    return execute_write(engine, statement) > 0
