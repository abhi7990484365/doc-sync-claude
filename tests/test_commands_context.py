"""TASK-018: command context, init-db and the D-24 startup-check table."""

import subprocess
import sys
from pathlib import Path

from employee_app.db.verify import verify_schema
from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.conftest import login_secret_for_tests, make_engine


def test_init_db_succeeds_on_empty_database_with_no_signing_key_or_departments(db_file: Path) -> None:
    env = cmd_env(db_file)
    assert "EMPLOYEE_APP_SECRET_KEY" not in env
    result = run_cli(["init-db"], env)
    assert result.exit_code == 0, result.output
    verify_schema(make_engine(db_file))


def test_init_db_is_repeatable(db_file: Path) -> None:
    env = cmd_env(db_file)
    assert run_cli(["init-db"], env).exit_code == 0
    assert run_cli(["init-db"], env).exit_code == 0


def test_user_commands_work_without_signing_key_or_departments(db_file: Path) -> None:
    env = cmd_env(db_file)
    run_cli(["init-db"], env)
    secret = login_secret_for_tests()
    assert run_cli(["create-user"], env, create_user_input("ops1", secret)).exit_code == 0
    assert run_cli(["unlock-user", "ops1"], env).exit_code == 0
    assert run_cli(["deactivate-user", "ops1"], env).exit_code == 0


def test_user_commands_refuse_a_database_without_the_schema(db_file: Path) -> None:
    env = cmd_env(db_file)
    for args, text in ((["create-user"], create_user_input("a", "b")), (["unlock-user", "a"], None),
                       (["deactivate-user", "a"], None)):
        result = run_cli(args, env, text)
        assert result.exit_code != 0
        assert "init-db" in result.output and "'user'" in result.output


def test_missing_database_setting_is_a_clear_error(db_file: Path) -> None:
    result = run_cli(["init-db"], {})
    assert result.exit_code != 0
    assert "EMPLOYEE_APP_DB_PATH" in result.output


def test_unreachable_database_directory_is_a_clear_error(tmp_path: Path) -> None:
    result = run_cli(["init-db"], cmd_env(tmp_path / "no-such-dir" / "x.sqlite3"))
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_output_contains_no_secret(db_file: Path) -> None:
    env = cmd_env(db_file, EMPLOYEE_APP_SECRET_KEY="fake-key-should-not-be-printed")
    result = run_cli(["init-db"], env)
    assert "fake-key-should-not-be-printed" not in result.output


def test_commands_never_import_the_web_factory() -> None:
    code = (
        "import sys, employee_app.commands; "
        "bad = [m for m in ('employee_app.app', 'flask', 'flask_login', 'flask_wtf') if m in sys.modules]; "
        "sys.exit(1 if bad else 0)"
    )
    src = Path(__file__).resolve().parents[1] / "src"
    result = subprocess.run([sys.executable, "-c", code], env={"PYTHONPATH": str(src), "SYSTEMROOT": "C:\\Windows"},
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
