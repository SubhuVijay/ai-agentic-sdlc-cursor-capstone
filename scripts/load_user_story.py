"""Load the user story into docs/user-story.md.

Sources, set in config/jira.local.json:

- file: keep or copy a markdown story already on disk
- jira: one Jira Cloud issue
- confluence: one Confluence Cloud page
- word: a .docx file

Copy config/jira.example.json to config/jira.local.json and set source.
With no local config, docs/user-story.md is left as it is.

    python scripts/load_user_story.py
    python scripts/load_user_story.py --word docs/incoming/user-story.docx

Never prints the API token.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "user-story.md"
CONFIG = ROOT / "config" / "jira.local.json"
JIRA_FIELDS = ("baseUrl", "email", "apiToken", "issueKey")
CONFLUENCE_FIELDS = ("baseUrl", "email", "apiToken", "pageId")
_HEADER_PREFIXES = ("**Jira:**", "**Type:**", "**Priority:**", "**Status:**", "**Component:**", "**Source:**", "**ID:**")
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load a user story into docs/user-story.md")
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--word", type=Path, help="Read this .docx instead of the configured source")
    args = parser.parse_args(argv)

    try:
        if args.word is not None:
            body = docx_to_markdown(args.word)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(stamp(f"Word document {args.word.name}", body), encoding="utf-8", newline="\n")
            print(f"Wrote {args.output} from {args.word}")
            return 0
        if not args.config.is_file():
            print("No config/jira.local.json. Using docs/user-story.md")
            return 0
        settings = load_config(args.config)
        return apply_config(settings, args.output, root=ROOT)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2


def load_config(path: Path) -> dict:
    """Read the local story source. Raise ValueError when the selected source is incomplete."""
    if not path.is_file():
        raise ValueError(
            "Missing config/jira.local.json. "
            "Copy config/jira.example.json to config/jira.local.json and set source. "
            "Do not commit the API token."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"config/jira.local.json is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("config/jira.local.json must be a JSON object.")

    if "source" not in data and "baseUrl" in data:
        data = {"source": "jira", "jira": data}
    source = str(data.get("source", "")).strip().lower()
    if source not in ("file", "jira", "confluence", "word"):
        raise ValueError("source in config/jira.local.json must be file, jira, confluence, or word.")

    settings = {
        "source": source,
        "file": str(data.get("file") or "docs/user-story.md").strip(),
        "jira": _block(data.get("jira"), JIRA_FIELDS, required=(source == "jira")),
        "confluence": _block(data.get("confluence"), CONFLUENCE_FIELDS, required=(source == "confluence")),
        "word": str((data.get("word") or {}).get("path") or "").strip() if isinstance(data.get("word"), dict) else "",
    }
    if source == "word" and not settings["word"]:
        raise ValueError("config/jira.local.json is missing: word.path.")
    for block_name in ("jira", "confluence"):
        block = settings[block_name]
        if block and not block["baseUrl"].startswith("https://"):
            raise ValueError(f"{block_name}.baseUrl in config/jira.local.json must start with https://")
    return settings


def _block(value, fields: tuple[str, ...], required: bool) -> dict | None:
    if not isinstance(value, dict):
        if required:
            raise ValueError("config/jira.local.json is missing: " + ", ".join(fields) + ".")
        return None
    cleaned = {name: str(value.get(name, "")).strip() for name in fields}
    if "baseUrl" in cleaned:
        cleaned["baseUrl"] = cleaned["baseUrl"].rstrip("/")
    missing = [name for name in fields if not cleaned[name]]
    if missing and required:
        raise ValueError(
            "config/jira.local.json is missing: " + ", ".join(missing) + ". Do not commit the API token."
        )
    if missing:
        return None
    return cleaned


def apply_config(settings: dict, output: Path, root: Path) -> int:
    source = settings["source"]
    if source == "file":
        incoming = (root / settings["file"]).resolve()
        if incoming != output.resolve():
            if not incoming.is_file():
                raise ValueError(f"Story file not found: {settings['file']}")
            output.write_text(incoming.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
            print(f"Wrote {output} from {settings['file']}")
        else:
            print(f"Using {settings['file']}")
        return 0
    if source == "word":
        path = (root / settings["word"]).resolve()
        body = docx_to_markdown(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(stamp(f"Word document {path.name}", body), encoding="utf-8", newline="\n")
        print(f"Wrote {output} from {settings['word']}")
        return 0
    if source == "jira":
        issue = fetch_jira(settings["jira"])
        body = adf_to_markdown(issue["description"]).strip()
        if not body:
            raise ValueError(f"{issue['key']} has an empty description.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            render(issue["key"], issue["summary"], issue["status"], issue["issueType"], body),
            encoding="utf-8",
            newline="\n",
        )
        print(f"Wrote {output}")
        print(f"key: {issue['key']}")
        print(f"type: {issue['issueType']}")
        print(f"status: {issue['status']}")
        print(f"summary: {issue['summary']}")
        return 0
    page = fetch_confluence(settings["confluence"])
    body = html_to_markdown(page["html"]).strip()
    if not body:
        raise ValueError(f"Confluence page {page['id']} has an empty body.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(stamp(f"Confluence {page['id']}", f"# {page['title']}\n\n{body}"), encoding="utf-8", newline="\n")
    print(f"Wrote {output}")
    print(f"page: {page['id']}")
    print(f"title: {page['title']}")
    return 0


def fetch_jira(settings: dict) -> dict:
    url = (
        f"{settings['baseUrl']}/rest/api/3/issue/{settings['issueKey']}"
        "?fields=summary,status,issuetype,description"
    )
    payload = _get_json(url, settings["email"], settings["apiToken"])
    fields = payload.get("fields") or {}
    return {
        "key": str(payload.get("key") or settings["issueKey"]),
        "summary": str(fields.get("summary") or "Untitled").strip(),
        "status": str((fields.get("status") or {}).get("name") or "Unknown"),
        "issueType": str((fields.get("issuetype") or {}).get("name") or "Story"),
        "description": fields.get("description"),
    }


def fetch_confluence(settings: dict) -> dict:
    base = settings["baseUrl"]
    if not base.endswith("/wiki"):
        base = base + "/wiki"
    url = f"{base}/rest/api/content/{settings['pageId']}?expand=body.storage"
    payload = _get_json(url, settings["email"], settings["apiToken"])
    storage = ((payload.get("body") or {}).get("storage") or {}).get("value") or ""
    return {
        "id": str(payload.get("id") or settings["pageId"]),
        "title": str(payload.get("title") or "Untitled").strip(),
        "html": storage,
    }


def _get_json(url: str, email: str, token: str) -> dict:
    credentials = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Basic {credentials}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        message = f"Atlassian returned HTTP {error.code}."
        if detail:
            message = message + " " + detail
        raise ValueError(message) from error
    except urllib.error.URLError as error:
        raise ValueError(f"Could not reach Atlassian: {error.reason}") from error


def stamp(source_label: str, body: str) -> str:
    body = body.strip()
    if not body.startswith("# "):
        body = f"# User story\n\n{body}"
    lines = body.splitlines()
    rest = lines[1:]
    while rest and (rest[0].strip() == "" or rest[0].startswith(_HEADER_PREFIXES)):
        rest.pop(0)
    header = f"**Source:** {source_label}\n"
    return lines[0] + "\n\n" + header + "\n" + "\n".join(rest).lstrip() + "\n"


def render(key: str, summary: str, status: str, issue_type: str, body: str) -> str:
    """Write the Jira description as the story, with a short header from Jira."""
    if not body.startswith("# "):
        body = f"# {key}: {summary}\n\n{body.lstrip()}"
    lines = body.splitlines()
    rest = lines[1:]
    while rest and (rest[0].strip() == "" or rest[0].startswith(_HEADER_PREFIXES)):
        rest.pop(0)
    header = f"**Jira:** {key} ({issue_type})\n**Status:** {status}\n"
    return lines[0] + "\n\n" + header + "\n" + "\n".join(rest).lstrip() + "\n"


def adf_to_markdown(node) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_markdown(child) for child in node)
    if not isinstance(node, dict):
        return ""

    kind = node.get("type")
    content = node.get("content") or []
    if kind == "text":
        return str(node.get("text") or "")
    if kind == "hardBreak":
        return "\n"
    if kind == "heading":
        level = int((node.get("attrs") or {}).get("level") or 1)
        title = adf_to_markdown(content).strip()
        return f"\n{'#' * min(level, 6)} {title}\n\n"
    if kind == "paragraph":
        return adf_to_markdown(content).rstrip() + "\n\n"
    if kind in ("bulletList", "orderedList"):
        items = []
        for index, child in enumerate(content, start=1):
            text = adf_to_markdown(child).strip()
            prefix = f"{index}. " if kind == "orderedList" else "- "
            items.append(prefix + text)
        return "\n".join(items) + "\n\n"
    if kind == "listItem":
        return adf_to_markdown(content).strip()
    if kind == "codeBlock":
        language = str((node.get("attrs") or {}).get("language") or "")
        code = adf_to_markdown(content).strip("\n")
        return f"\n```{language}\n{code}\n```\n\n"
    if kind == "blockquote":
        inner = adf_to_markdown(content).strip()
        quoted = "\n".join("> " + line if line else ">" for line in inner.splitlines())
        return quoted + "\n\n"
    if kind == "rule":
        return "\n---\n\n"
    return adf_to_markdown(content)


class _HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        if tag in ("h1", "h2", "h3", "h4"):
            self.parts.append("\n\n" + ("#" * int(tag[1])) + " ")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag in ("p", "div", "tr"):
            self.parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def html_to_markdown(html: str) -> str:
    parser = _HTMLText()
    parser.feed(html or "")
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line).strip() + "\n"


def docx_to_markdown(path: Path) -> str:
    if path.suffix.lower() != ".docx":
        raise ValueError(f"{path.name} is not a .docx file. Save the Word document as .docx and run again.")
    if not path.is_file():
        raise ValueError(f"Word document not found: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            document = archive.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError) as error:
        raise ValueError(f"{path.name} is not a readable Word document.") from error
    root = ET.fromstring(document)
    paragraphs: list[str] = []
    for paragraph in root.iter(_W + "p"):
        style = ""
        properties = paragraph.find(_W + "pPr")
        if properties is not None:
            style_node = properties.find(_W + "pStyle")
            if style_node is not None:
                style = style_node.get(_W + "val") or ""
        line = "".join(node.text or "" for node in paragraph.iter(_W + "t")).strip()
        if not line:
            continue
        if style.lower().startswith("heading"):
            digits = "".join(character for character in style if character.isdigit()) or "1"
            line = "#" * min(int(digits), 6) + " " + line
        paragraphs.append(line)
    if not paragraphs:
        raise ValueError(f"{path.name} has no text.")
    return "\n\n".join(paragraphs) + "\n"


if __name__ == "__main__":
    sys.exit(main())
