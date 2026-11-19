# Step 1 — Requirements

1. Load the story, then read it.
   - Run `python scripts/load_user_story.py`.
   - Do not open `config/jira.local.json` and do not print tokens. The script reads that file.
   - `source` may be `jira`, `confluence`, `word`, or `file`. A Word file can also be loaded with `python scripts/load_user_story.py --word <path-to.docx>`.
   - If there is no local config, keep the story already in `docs/user-story.md`.
   - If the script fails, report its error message in the handoff as a blocker. Do not guess the story.
2. Read `docs/user-story.md`. Ask the open questions in that story. Add any question that would change scope, data, or failure behavior. Number the questions. Stop and wait.
3. After the user answers, create `.cursor/artifacts/requirements-agent/` if needed and write `.cursor/artifacts/requirements-agent/requirements.md` there. Do not write it at the repository root. Include:
   - Context and goal
   - Functional requirements (`FR-1`, ...)
   - Non-functional requirements (`NFR-1`, ...)
   - Acceptance criteria
   - Error and edge cases: a bad window value, a missing hold, a missing `readySince`, an empty overdue list, and `Not Found` phones
   - Out of scope
   - Decisions taken from the user's answers
4. Return the handoff. Commit only after the user approves it and asks for the commit.
