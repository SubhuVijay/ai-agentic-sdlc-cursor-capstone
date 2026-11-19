# Prompt — Step 3 Design review

Paste this into a Cursor Agent chat after the architecture is written.

---

You are the orchestrator. Delegate Step 3 to the `design-reviewer` sub-agent using the `agentic-sdlc` skill.

Have it review `.cursor/artifacts/architect/architecture.md` against `.cursor/artifacts/requirements-agent/requirements.md` and write `.cursor/artifacts/design-reviewer/design-review.md`. Show me the findings and wait. Resume it to update the architecture only for decisions I agree to. Do not write production code.
