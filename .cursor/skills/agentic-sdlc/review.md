# Step 6 — Code review

Prerequisite: the approved implementation tasks for this review are in the tree.

Review the implementation as a peer. Read `.cursor/artifacts/requirements-agent/requirements.md` before judging behavior. Create `.cursor/artifacts/code-reviewer/` if needed and write `.cursor/artifacts/code-reviewer/code-review.md` there, not at the repository root, with one section per review area. For each area, answer the question, cite the file or test that supports the answer, and mark the result pass or fix.

Evaluate each area:

| Review Area | Review Question |
| --- | --- |
| Correctness | Does each component behave as specified in the requirements? |
| Security | Are secrets excluded from output? Is user input validated? |
| Error Handling | Are bad input, a missing hold, and an empty overdue list handled gracefully? |
| Test Coverage | Do tests cover the happy path AND the 'Not Found' / missing-field edge cases? |
| Code Clarity | Are function names self-explanatory? Is logic easy to follow without comments? |
| DRY Principle | Is there duplicated logic that could be refactored into a shared function? |
| Dependency Safety | Are any known-vulnerable package versions in use? |

Fix blockers the user agrees to, then update `.cursor/artifacts/code-reviewer/code-review.md`. Do not open a pull request in this step.
