# Prompt — Step 6 Code review

Paste this into a Cursor Agent chat after the implementation you want reviewed is in the tree.

---

You are the orchestrator. Delegate Step 6 to the `code-reviewer` sub-agent using the `agentic-sdlc` skill.

Have it review the implementation as a peer and write `.cursor/artifacts/code-reviewer/code-review.md`. It evaluates each area:

| Review Area | Review Question |
| --- | --- |
| Correctness | Does each component behave as specified in the requirements? |
| Security | Are secrets excluded from output? Is user input validated? |
| Error Handling | Are bad input, a missing hold, and an empty overdue list handled gracefully? |
| Test Coverage | Do tests cover the happy path AND the 'Not Found' / missing-field edge cases? |
| Code Clarity | Are function names self-explanatory? Is logic easy to follow without comments? |
| DRY Principle | Is there duplicated logic that could be refactored into a shared function? |
| Dependency Safety | Are any known-vulnerable package versions in use? |

Show me the handoff. Cite the file or test for each answer. Do not open a pull request.
