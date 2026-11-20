"""C-6 user queries: reads return plain value objects (no detached ORM rows)."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from employee_app.db.engine import session_scope
from employee_app.db.models import ROLE_HR_ADMINISTRATOR, User
from employee_app.db.statements import execute_write


@dataclass(frozen=True)
class UserView:
    id: int
    username_normalized: str
    password_hash: str = ""
    role: str = ROLE_HR_ADMINISTRATOR
    is_active: bool = True
    auth_version: int = 0
    failed_login_count: int = 0
    locked_until: datetime | None = None

    def is_locked(self, now: datetime) -> bool:
        return self.locked_until is not None and self.locked_until > now


def _view(row: User) -> UserView:
    return UserView(
        id=row.id,
        username_normalized=row.username_normalized,
        password_hash=row.password_hash,
        role=row.role,
        is_active=row.is_active,
        auth_version=row.auth_version,
        failed_login_count=row.failed_login_count,
        locked_until=row.locked_until,
    )


def _first_view(session: Session, *conditions: object) -> UserView | None:
    row = session.execute(select(User).where(*conditions)).scalar_one_or_none()  # type: ignore[arg-type]
    return None if row is None else _view(row)


def find_user_by_username(engine: Engine, username_normalized: str) -> UserView | None:
    with session_scope(engine) as session:
        return _first_view(session, User.username_normalized == username_normalized)


def get_user(engine: Engine, user_id: int) -> UserView | None:
    with session_scope(engine) as session:
        return _first_view(session, User.id == user_id)


def insert_user(
    engine: Engine, username: str, username_normalized: str, password_hash: str, created_at: datetime
) -> int:
    """Create an HR Administrator (auth_version 0). Raises IntegrityConflict
    when the normalised username exists."""
    with session_scope(engine, write=True) as session:
        row = User(
            username=username,
            username_normalized=username_normalized,
            password_hash=password_hash,
            role=ROLE_HR_ADMINISTRATOR,
            is_active=True,
            auth_version=0,
            failed_login_count=0,
            created_at=created_at,
        )
        session.add(row)
        session.commit()
        return row.id


def deactivate_user_by_id(engine: Engine, user_id: int) -> bool:
    """Set is_active false and bump auth_version in one statement."""
    statement = (
        update(User).where(User.id == user_id).values(is_active=False, auth_version=User.auth_version + 1)
    )
    return execute_write(engine, statement) > 0


def increment_auth_version(engine: Engine, user_id: int, expected: int | None = None) -> bool:
    """Atomic ``auth_version = auth_version + 1``. With ``expected`` the bump
    only happens if the stored value still matches (used by logout)."""
    conditions = [User.id == user_id]
    if expected is not None:
        conditions.append(User.auth_version == expected)
    statement = update(User).where(*conditions).values(auth_version=User.auth_version + 1)
    return execute_write(engine, statement) > 0
