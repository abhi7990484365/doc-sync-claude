"""Helpers for driving the operator commands with the Click test runner."""

from pathlib import Path

from click.testing import CliRunner, Result

from employee_app import config
from employee_app.commands import cli


def cmd_env(db_file: Path, **extra: str) -> dict[str, str]:
    """Environment for commands: only the database location (no signing key)."""
    return {config.ENV_DB_PATH: str(db_file), **extra}


def run_cli(args: list[str], env: dict[str, str], user_input: str | None = None) -> Result:
    return CliRunner().invoke(cli, args, input=user_input, env=env)


def create_user_input(username: str, secret: str, confirm: str | None = None) -> str:
    return f"{username}\n{secret}\n{secret if confirm is None else confirm}\n"
