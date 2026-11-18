import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_module_missing_path_exits_2(tmp_path: Path) -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "doc_sync", str(tmp_path / "missing")],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 2
    assert "REPO_PATH not found:" in result.stderr
    assert "Traceback" not in result.stderr
