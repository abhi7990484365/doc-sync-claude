"""C-6 engine and session lifecycle.

Settings (verified in tests/test_lib_sqlite.py): parameters hidden in errors
(D-21), busy wait from configuration (D-20), foreign keys on, write-ahead
journal (D-25 Proposal), and an explicit transaction-begin mode so a write
transaction can begin as a write (``BEGIN IMMEDIATE``).
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL, Connection, Engine
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from employee_app.config import DatabaseSettings
from employee_app.db.errors import IntegrityConflict, StorageError

BEGIN_OPTION = "sqlite_begin"
IMMEDIATE = "IMMEDIATE"


def _on_connect(dbapi_conn: Any, _record: Any) -> None:
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def _on_begin(conn: Connection) -> None:
    mode = conn.get_execution_options().get(BEGIN_OPTION, "DEFERRED")
    conn.exec_driver_sql(f"BEGIN {mode}")


def create_db_engine(settings: DatabaseSettings) -> Engine:
    """Create the engine. Does not touch the file until first use."""
    engine = create_engine(
        URL.create("sqlite", database=settings.database_path),
        hide_parameters=True,
        connect_args={"timeout": settings.busy_timeout_seconds, "isolation_level": None},
    )
    event.listen(engine, "connect", _on_connect)
    event.listen(engine, "begin", _on_begin)
    return engine


def write_engine(engine: Engine) -> Engine:
    """Engine view whose transactions begin as writes (D-25)."""
    return engine.execution_options(**{BEGIN_OPTION: IMMEDIATE})


def classify_error(exc: SQLAlchemyError) -> StorageError:
    """Map a SQLAlchemy error to a StorageError carrying only a category."""
    if isinstance(exc, IntegrityError):
        return IntegrityConflict()
    category = type(exc.orig).__name__ if isinstance(exc, DBAPIError) and exc.orig else type(exc).__name__
    return StorageError(category)


@contextmanager
def session_scope(engine: Engine, *, write: bool = False) -> Iterator[Session]:
    """Short-lived session: always closed, uncommitted work rolled back.

    The caller commits explicitly. SQLAlchemy errors become StorageError.
    """
    session = Session(write_engine(engine) if write else engine, expire_on_commit=False)
    try:
        yield session
    except SQLAlchemyError as exc:
        session.rollback()
        raise classify_error(exc) from None
    finally:
        session.close()


def check_reachable(engine: Engine) -> None:
    """Raise StorageError if the database cannot be opened and queried."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise classify_error(exc) from None
