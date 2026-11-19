import json
import subprocess
import sys
import unittest

from hook_loader import ROOT, load_hook

guard_shell = load_hook("guard_shell")


class GuardShellTests(unittest.TestCase):
    def test_ordinary_git_commands_are_allowed(self):
        for command in (
            "git status",
            "git push -u origin HEAD",
            "git push origin feature-flag",
            "git clean -n",
            "git reset HEAD",
        ):
            with self.subTest(command=command):
                self.assertEqual(guard_shell.decide(command)["permission"], "allow")

    def test_secret_reads_are_denied(self):
        for command in (
            "cat .env",
            "Get-Content .env.local",
            "type .env",
            "printenv",
            "Get-ChildItem Env:",
            "cat config/jira.local.json",
            "Get-Content config\\jira.local.json",
        ):
            with self.subTest(command=command):
                self.assertEqual(guard_shell.decide(command)["permission"], "deny")

    def test_env_example_read_is_allowed(self):
        self.assertEqual(guard_shell.decide("cat .env.example")["permission"], "allow")
        self.assertEqual(guard_shell.decide("Get-Content .env.sample")["permission"], "allow")
        self.assertEqual(guard_shell.decide("cat config/jira.example.json")["permission"], "allow")
        self.assertEqual(guard_shell.decide("python scripts/load_user_story.py")["permission"], "allow")

    def test_destructive_git_asks_for_confirmation(self):
        for command in (
            "git push --force",
            "git push --force-with-lease",
            "git push origin main -f",
            "git reset --hard",
            "git clean -fd",
            "git clean --force",
        ):
            with self.subTest(command=command):
                self.assertEqual(guard_shell.decide(command)["permission"], "ask")

    def test_cli_allows_git_status(self):
        script = ROOT / ".cursor" / "hooks" / "guard_shell.py"
        completed = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps({"command": "git status", "cwd": ".", "sandbox": False}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["permission"], "allow")


if __name__ == "__main__":
    unittest.main()
