"""C-10 Click group: init-db, create-user, deactivate-user, unlock-user.

Credentials are never accepted from options or environment variables: the
password is read only from a hidden interactive prompt, typed twice.
"""

import click

from employee_app.commands import accounts
from employee_app.commands.context import build_context
from employee_app.logging_setup import configure_logging


@click.group()
def cli() -> None:
    """Operator commands for the Add Employee application."""
    configure_logging()


@cli.command("init-db")
def init_db() -> None:
    """Create (or verify) the database schema."""
    accounts.init_database(build_context(require_schema=False))
    click.echo("Database schema is ready.")


@cli.command("create-user")
def create_user() -> None:
    """Create an HR Administrator (username and password are prompted)."""
    context = build_context()
    username = click.prompt("Username")
    password = click.prompt(
        "Password", hide_input=True, confirmation_prompt=True, default="", show_default=False
    )
    accounts.create_account(context, username, password)
    click.echo("User created.")


@cli.command("deactivate-user")
@click.argument("username")
def deactivate_user(username: str) -> None:
    """Deactivate an account; open sessions end on their next request."""
    accounts.deactivate_account(build_context(), username)
    click.echo("User deactivated.")


@cli.command("unlock-user")
@click.argument("username")
def unlock_user(username: str) -> None:
    """Clear the failed-login count and lock of an account."""
    accounts.unlock_account(build_context(), username)
    click.echo("User unlocked.")
