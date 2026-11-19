# Prompt — Step 5 Implementation

Paste this into a Cursor Agent chat and name the approved task.

---

You are the orchestrator. Delegate Step 5 to the `implementer` sub-agent using the `agentic-sdlc` skill.

Pass only the task I name from `.cursor/artifacts/planner/impl-plan.md`. Have it follow the requirements, architecture, and design review in `.cursor/artifacts/`, extend `src/holdshelf`, and add tests for the happy path and for missing-field / `Not Found` cases. Show me the files it changed and wait.
