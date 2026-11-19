# Prompt — Step 7 Verify

Paste this into a Cursor Agent chat after code review blockers are resolved.

---

You are the orchestrator. Delegate Step 7 to the `verifier` sub-agent using the `agentic-sdlc` skill.

Have it run the full test suite, check the hold shelf against the requirements for the overdue rules, `Not Found` phones, and leaked secrets, and write `.cursor/artifacts/verifier/verification-report.md`. It fixes in-scope failures and re-runs before it reports success. Show me the handoff.
