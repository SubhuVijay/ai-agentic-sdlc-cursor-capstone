#!/usr/bin/env python3
"""beforeReadFile hook: block credential and secret files."""

import json
import sys
from pathlib import Path

ALLOWED_ENV_NAMES = {".env.example", ".env.sample"}
KEY_NAMES = {"credentials.json", "id_rsa", "id_dsa", "id_ed25519", "id_ecdsa"}
KEY_SUFFIXES = (".pem", ".p12", ".pfx", ".key")

ALLOW = {"permission": "allow"}


def is_sensitive(file_path: str) -> bool:
    path = Path(file_path)
    name = path.name.lower()
    if name in ALLOWED_ENV_NAMES:
        return False
    if name == ".env" or name.startswith(".env."):
        return True
    if name in KEY_NAMES or name.endswith(KEY_SUFFIXES):
        return True
    return ".ssh" in {part.lower() for part in path.parts}


def decide(file_path: str) -> dict:
    if is_sensitive(file_path):
        return {
            "permission": "deny",
            "user_message": "Blocked a read of a secret or credential file.",
        }
    return dict(ALLOW)


def main() -> None:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    file_path = payload.get("file_path", "")
    if not isinstance(file_path, str):
        file_path = ""
    json.dump(decide(file_path), sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump(ALLOW, sys.stdout)
        sys.stdout.write("\n")
