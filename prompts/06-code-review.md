# Prompt — Step 6 Code review

Paste this into a Cursor Agent chat after the implementation you want reviewed is in the tree.

---

Run Agentic SDLC Step 6 (Review) using the `agentic-sdlc` skill.

Review the implementation as a peer and write `code-review.md`. Evaluate each area:

| Review Area | Review Question |
| --- | --- |
| Correctness | Does each component behave as specified in requirements.md? |
| Security | Are secrets excluded from output? Is user input validated? |
| Error Handling | Are all API failures, missing files, and empty repos handled gracefully? |
| Test Coverage | Do tests cover the happy path AND the 'Not Found' / missing-field edge cases? |
| Code Clarity | Are function names self-explanatory? Is logic easy to follow without comments? |
| DRY Principle | Is there duplicated logic that Copilot can refactor into a shared function? |
| Dependency Safety | Does Copilot flag any known-vulnerable package versions? |

Cite the file or test for each answer. Do not open a pull request.
