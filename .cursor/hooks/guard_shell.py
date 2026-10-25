#!/usr/bin/env python3
"""beforeShellExecution hook: gate destructive git and secret dumps."""

import json
import re
import sys

READ_VERBS = re.compile(
    r"\b(type|cat|more|less|head|tail|gc|Get-Content|Select-String)\b",
    re.IGNORECASE,
)
DUMP_ENV = re.compile(
    r"\bprintenv\b|Get-ChildItem\s+Env:|gci\s+Env:|ls\s+Env:",
    re.IGNORECASE,
)
GIT_PUSH = re.compile(r"\bgit(\.exe)?\s+(-C\s+\S+\s+)?push\b", re.IGNORECASE)
GIT_RESET_HARD = re.compile(
    r"\bgit(\.exe)?\s+(-C\s+\S+\s+)?reset\s+--hard\b",
    re.IGNORECASE,
)
GIT_CLEAN_FORCE = re.compile(
    r"\bgit(\.exe)?\s+(-C\s+\S+\s+)?clean\b[^\n]*(\s-\w*f\w*|\s--force\b)",
    re.IGNORECASE,
)
FORCE_FLAG = re.compile(
    r"(?<![\w-])(--force-with-lease|--force)(?![\w-])|\s-\w*f\w*"
)

ALLOW = {"permission": "allow"}


def reads_dotenv(command: str) -> bool:
    if READ_VERBS.search(command) is None:
        return False
    scrubbed = re.sub(r"\.env\.(example|sample)\b", "", command, flags=re.IGNORECASE)
    return re.search(r"\.env\b", scrubbed, re.IGNORECASE) is not None


def is_force_push(command: str) -> bool:
    match = GIT_PUSH.search(command)
    if match is None:
        return False
    return FORCE_FLAG.search(command[match.end() :]) is not None


def decide(command: str) -> dict:
    if reads_dotenv(command) or DUMP_ENV.search(command) is not None:
        return {
            "permission": "deny",
            "user_message": "Blocked a command that would print secrets or environment values.",
            "agent_message": "Do not read .env files or dump the environment. .env.example is safe to read.",
        }
    if is_force_push(command) or GIT_RESET_HARD.search(command) or GIT_CLEAN_FORCE.search(command):
        return {
            "permission": "ask",
            "user_message": "This command can rewrite history or delete files. Confirm before continuing.",
            "agent_message": "A hook asked for confirmation before a destructive git command.",
        }
    return dict(ALLOW)


def main() -> None:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    command = payload.get("command", "")
    if not isinstance(command, str):
        command = ""
    json.dump(decide(command), sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump(ALLOW, sys.stdout)
        sys.stdout.write("\n")
