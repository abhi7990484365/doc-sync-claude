"""PostToolUse: run pytest after an Edit/Write on src/ or tests/."""
import json
import subprocess
import sys


def main() -> int:
    data = json.load(sys.stdin)
    path = data.get("tool_input", {}).get("file_path", "")
    if "/src/" not in path and "/tests/" not in path:
        return 0
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True
    )
    if result.returncode in (0, 5):  # 5 = no tests collected yet
        return 0
    print(result.stdout[-3000:], file=sys.stderr)
    return 2  # feed failures back to Claude


if __name__ == "__main__":
    sys.exit(main())
