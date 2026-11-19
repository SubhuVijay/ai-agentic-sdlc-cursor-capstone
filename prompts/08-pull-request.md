# Prompt — Step 8 Pull request

Paste this into a Cursor Agent chat after verification passes. The agent prepares the description first, then opens the pull request when you confirm.

---

You are the orchestrator. Delegate Step 8 to the `release-agent` sub-agent using the `agentic-sdlc` skill.

Have it update `CHANGELOG.md` and write the pull request description to `.cursor/artifacts/release-agent/pull-request.md` from `.github/PULL_REQUEST_TEMPLATE.md`. The description must include all of these sections:

- Summary — 2-3 sentence overview of what was built and why.
- Changes Made — bulleted list of all files added/modified and the reason.
- Test Evidence — paste the test run output or link to CI results.
- Known Limitations — anything marked 'Not Found' or out of scope.
- Reviewer Checklist — a tick-list the reviewer must complete before approving.

Show me the description and wait for confirmation before the sub-agent pushes or opens the pull request.
