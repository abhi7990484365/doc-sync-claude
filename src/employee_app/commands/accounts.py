"""C-10 account operations. Pure of Click prompts; they raise CommandError.

Operator actions are logged as one line with the command name, affected user
id and an outcome category only (NR-15): never a username, password or hash.
"""

import logging
from collections.abc import Callable

from employee_app import clock
from employee_app.commands.context import CommandContext, CommandError
from employee_app.db import create_schema
from employee_app.db.errors import IntegrityConflict, SchemaVerificationError, StorageError
from employee_app.db.lockout import unlock
from employee_app.db.users import UserView, deactivate_user_by_id, find_user_by_username, insert_user
from employee_app.db.verify import verify_schema
from employee_app.logging_setup import log_event
from employee_app.security import hash_password
from employee_app.validation import validate_password
from employee_app.validation.username import normalize_username, validate_username


def _log(command: str, outcome: str, user_id: int | None = None) -> None:
    fields: dict[str, int | str] = {"command": command, "outcome": outcome}
    if user_id is not None:
        fields["user_id"] = user_id
    log_event(logging.INFO, "operator_command", **fields)


def _storage_failure(command: str, exc: StorageError) -> CommandError:
    _log(command, "storage_error")
    return CommandError(f"Database error ({exc.category}); no change was made")


def init_database(context: CommandContext) -> None:
    """Create the schema (repeatable) and verify it afterwards."""
    try:
        create_schema(context.engine)
        verify_schema(context.engine)
    except StorageError as exc:
        raise _storage_failure("init-db", exc) from None
    except SchemaVerificationError as exc:
        _log("init-db", "verification_failed")
        raise CommandError(str(exc)) from None
    _log("init-db", "ok")


def _check_new_account(context: CommandContext, username: str, password: str) -> str:
    """Validate inputs and return the cleaned username or raise CommandError."""
    cleaned, username_error = validate_username(username)
    if username_error:
        _log("create-user", "rejected")
        raise CommandError(f"Username rejected: {username_error}")
    password_error = validate_password(password, context.settings.password_min_length)
    if password_error:
        _log("create-user", "rejected")
        raise CommandError(f"Password rejected: {password_error}")
    return cleaned


def create_account(context: CommandContext, username: str, password: str) -> int:
    """Create an HR Administrator; returns the new user id."""
    cleaned = _check_new_account(context, username, password)
    try:
        user_id = insert_user(
            context.engine, cleaned, normalize_username(cleaned), hash_password(password), clock.utc_now()
        )
    except IntegrityConflict:
        _log("create-user", "duplicate")
        raise CommandError("Username already exists (usernames are case-insensitive)") from None
    except StorageError as exc:
        raise _storage_failure("create-user", exc) from None
    _log("create-user", "created", user_id)
    return user_id


def _require_user(context: CommandContext, command: str, username: str) -> UserView:
    try:
        user = find_user_by_username(context.engine, normalize_username(username))
    except StorageError as exc:
        raise _storage_failure(command, exc) from None
    if user is None:
        _log(command, "unknown_user")
        raise CommandError("Unknown username; no change was made")
    return user


def _apply(command: str, context: CommandContext, username: str, action: Callable[[int], bool]) -> int:
    user = _require_user(context, command, username)
    try:
        action(user.id)
    except StorageError as exc:
        raise _storage_failure(command, exc) from None
    _log(command, "ok", user.id)
    return user.id


def deactivate_account(context: CommandContext, username: str) -> int:
    """Set is_active false and bump auth_version (ends open sessions)."""
    return _apply("deactivate-user", context, username, lambda uid: deactivate_user_by_id(context.engine, uid))


def unlock_account(context: CommandContext, username: str) -> int:
    """Clear failed-login count and lock (FR-18). Idempotent."""
    return _apply("unlock-user", context, username, lambda uid: unlock(context.engine, uid))
