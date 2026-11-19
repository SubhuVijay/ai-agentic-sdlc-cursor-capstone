import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_story_module():
    path = ROOT / "scripts" / "load_user_story.py"
    spec = importlib.util.spec_from_file_location("load_user_story", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


loader = load_story_module()


class StorySourceTests(unittest.TestCase):
    def test_missing_file_names_the_example(self):
        missing = Path(tempfile.gettempdir()) / "does-not-exist-jira.local.json"
        with self.assertRaises(ValueError) as raised:
            loader.load_config(missing)
        self.assertIn("config/jira.example.json", str(raised.exception))

    def test_blank_jira_token_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jira.local.json"
            path.write_text(
                json.dumps(
                    {
                        "source": "jira",
                        "jira": {
                            "baseUrl": "https://example.atlassian.net",
                            "email": "dev@example.com",
                            "apiToken": "  ",
                            "issueKey": "HOLD-21",
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError) as raised:
                loader.load_config(path)
        self.assertIn("apiToken", str(raised.exception))

    def test_flat_jira_config_strips_the_base_url(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jira.local.json"
            path.write_text(
                json.dumps(
                    {
                        "baseUrl": "https://example.atlassian.net/",
                        "email": " dev@example.com ",
                        "apiToken": "token-value",
                        "issueKey": "HOLD-21",
                    }
                ),
                encoding="utf-8",
            )
            settings = loader.load_config(path)
        self.assertEqual(settings["source"], "jira")
        self.assertEqual(settings["jira"]["baseUrl"], "https://example.atlassian.net")
        self.assertEqual(settings["jira"]["email"], "dev@example.com")
        self.assertEqual(settings["jira"]["issueKey"], "HOLD-21")

    def test_file_source_does_not_need_a_token(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jira.local.json"
            path.write_text(json.dumps({"source": "file", "file": "docs/user-story.md"}), encoding="utf-8")
            settings = loader.load_config(path)
        self.assertEqual(settings["source"], "file")
        self.assertIsNone(settings["jira"])

    def test_missing_config_leaves_the_story_in_place(self):
        missing = Path(tempfile.gettempdir()) / "no-such-jira-config.json"
        self.assertEqual(loader.main(["--config", str(missing)]), 0)

    def test_word_document_becomes_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "story.docx"
            output = root / "user-story.md"
            _write_docx(document, "Heading1", "Show holds that have waited too long", "List ready holds past the pickup window.")
            code = loader.main(["--word", str(document), "--output", str(output)])
            text = output.read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("# Show holds that have waited too long", text)
        self.assertIn("**Source:** Word document story.docx", text)
        self.assertIn("List ready holds past the pickup window.", text)

    def test_confluence_storage_becomes_text(self):
        html = "<h1>Story</h1><p>Show overdue holds.</p><ul><li>Not Found</li></ul><script>secret</script>"
        text = loader.html_to_markdown(html)
        self.assertIn("# Story", text)
        self.assertIn("Show overdue holds.", text)
        self.assertIn("- Not Found", text)
        self.assertNotIn("secret", text)

    def test_example_config_has_no_token(self):
        data = json.loads((ROOT / "config" / "jira.example.json").read_text(encoding="utf-8"))
        self.assertEqual(data["jira"]["apiToken"], "")
        self.assertEqual(data["confluence"]["apiToken"], "")
        self.assertEqual(data["source"], "file")


def _write_docx(path: Path, style: str, heading: str, paragraph: str) -> None:
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t>{heading}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)


if __name__ == "__main__":
    unittest.main()
