"""PreToolUse: block pushes to main and commands that write secret-like strings."""
import json
import re
import sys

PUSH_MAIN = re.compile(r"git\s+push\b[^\n;&|]*(\bmain\b|\bmaster\b)")
SECRETS = re.compile(r"ghp_|github_pat_|password\s*=", re.IGNORECASE)


def violation(command: str) -> str:
    if PUSH_MAIN.search(command):
        return "Blocked: pushing to main is not allowed. Use feature/doc-sync."
    if SECRETS.search(command):
        return "Blocked: command contains a secret-like string. Use environment variables."
    return ""


def main() -> int:
    data = json.load(sys.stdin)
    message = violation(data.get("tool_input", {}).get("command", ""))
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
