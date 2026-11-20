"""Shared helper: run one statement in its own short write transaction."""

from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import Executable

from employee_app.db.engine import classify_error, write_engine


def execute_write(engine: Engine, statement: Executable) -> int:
    """Run ``statement`` in its own transaction that begins as a write and
    commits. Returns the number of rows changed. Raises StorageError."""
    try:
        with write_engine(engine).begin() as conn:
            return int(conn.execute(statement).rowcount)
    except SQLAlchemyError as exc:
        raise classify_error(exc) from None
