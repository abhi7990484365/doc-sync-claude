"""C-6 Persistence: models, engine, schema verification, queries."""

from sqlalchemy.engine import Engine

from employee_app.db.models import Base


def create_schema(engine: Engine) -> None:
    """Create all tables and indexes (idempotent)."""
    Base.metadata.create_all(engine)
