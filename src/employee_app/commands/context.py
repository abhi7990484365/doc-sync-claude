"""C-10 command context (D-24).

Loads only the database settings group and C-6. It never calls the web
application factory, so no web-only startup check can block a command.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

import click
from sqlalchemy.engine import Engine

from employee_app.config import ConfigError, CoreSettings, load_core_settings
from employee_app.db.engine import check_reachable, create_db_engine
from employee_app.db.errors import SchemaVerificationError, StorageError
from employee_app.db.verify import verify_schema


class CommandError(click.ClickException):
    """Clear operator-facing failure (non-zero exit). Never carries secrets."""


@dataclass(frozen=True)
class CommandContext:
    settings: CoreSettings
    engine: Engine


def build_context(env: Mapping[str, str] | None = None, *, require_schema: bool = True) -> CommandContext:
    """Create the context. ``init-db`` passes ``require_schema=False``."""
    try:
        settings = load_core_settings(os.environ if env is None else env)
    except ConfigError as exc:
        raise CommandError(str(exc)) from None
    engine = create_db_engine(settings.database)
    try:
        check_reachable(engine)
        if require_schema:
            verify_schema(engine)
    except StorageError as exc:
        raise CommandError(f"Database is not reachable ({exc.category})") from None
    except SchemaVerificationError as exc:
        raise CommandError(f"{exc}. Run init-db first.") from None
    return CommandContext(settings=settings, engine=engine)
