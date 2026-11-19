# Prompt — Step 1 Requirements

Paste this into a new Cursor Agent chat. To pull the story from Jira, first copy `config/jira.example.json` to `config/jira.local.json`, set `source` to `jira`, and fill in the Jira block. Without that file, the existing `docs/user-story.md` is used.

---

You are the orchestrator. Delegate Step 1 to the `requirements-agent` sub-agent using the `agentic-sdlc` skill.

Have it run `python scripts/load_user_story.py` to load the story from Jira, Confluence, Word, or file, then read `docs/user-story.md`. Show me the questions it returns and wait. After I answer, resume that sub-agent so it can write `.cursor/artifacts/requirements-agent/requirements.md`. Do not commit until I ask.
