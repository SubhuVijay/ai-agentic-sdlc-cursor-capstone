import json
import subprocess
import sys
import unittest

from hook_loader import ROOT, load_hook

guard_secrets = load_hook("guard_secrets")


class GuardSecretsTests(unittest.TestCase):
    def test_project_files_are_allowed(self):
        for path in (
            r"C:\repo\src\main.py",
            "/repo/README.md",
            r"C:\repo\.env.example",
            "/repo/.env.sample",
            r"C:\repo\tests\test_guard_secrets.py",
        ):
            with self.subTest(path=path):
                self.assertEqual(guard_secrets.decide(path)["permission"], "allow")

    def test_secret_files_are_denied(self):
        for path in (
            r"C:\repo\.env",
            r"C:\repo\.env.local",
            "/repo/secrets/credentials.json",
            r"C:\Users\me\.ssh\id_rsa",
            "/repo/certs/server.pem",
            r"C:\repo\config\app.key",
        ):
            with self.subTest(path=path):
                self.assertEqual(guard_secrets.decide(path)["permission"], "deny")

    def test_cli_denies_dotenv(self):
        script = ROOT / ".cursor" / "hooks" / "guard_secrets.py"
        completed = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps({"file_path": "/repo/.env", "content": "TOKEN=1"}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["permission"], "deny")


if __name__ == "__main__":
    unittest.main()
