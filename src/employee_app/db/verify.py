"""C-6 schema verification (D-19, D-24). Messages name objects, never values."""

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from employee_app.db.engine import classify_error
from employee_app.db.errors import SchemaVerificationError

REQUIRED_TABLES = ("user", "employee", "audit_record")
REQUIRED_UNIQUE = (
    ("employee", "email_normalized"),
    ("user", "username_normalized"),
    ("audit_record", "employee_id"),
)


def _has_unique_index(indexes: list[dict], column: str) -> bool:  # type: ignore[type-arg]
    return any(ix.get("unique") and ix.get("column_names") == [column] for ix in indexes)


def find_schema_problems(engine: Engine) -> list[str]:
    """Return one message per missing required table or unique index."""
    try:
        inspector = inspect(engine)
        existing = set(inspector.get_table_names())
        problems = [f"Required table '{name}' is missing" for name in REQUIRED_TABLES if name not in existing]
        for table, column in REQUIRED_UNIQUE:
            if table in existing and not _has_unique_index(inspector.get_indexes(table), column):
                problems.append(f"Required unique index on {table}.{column} is missing")
    except SQLAlchemyError as exc:
        raise classify_error(exc) from None
    return problems


def verify_schema(engine: Engine) -> None:
    """Raise SchemaVerificationError listing every problem found."""
    problems = find_schema_problems(engine)
    if problems:
        raise SchemaVerificationError("; ".join(problems))
