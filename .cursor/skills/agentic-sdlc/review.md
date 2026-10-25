# Step 6 — Code review

Prerequisite: the approved implementation tasks for this review are in the tree.

Review the implementation as a peer. Read `requirements.md` before judging behavior. Write `code-review.md` with one section per review area. For each area, answer the question, cite the file or test that supports the answer, and mark the result pass or fix.

Evaluate each area:

| Review Area | Review Question |
| --- | --- |
| Correctness | Does each component behave as specified in requirements.md? |
| Security | Are secrets excluded from output? Is user input validated? |
| Error Handling | Are all API failures, missing files, and empty repos handled gracefully? |
| Test Coverage | Do tests cover the happy path AND the 'Not Found' / missing-field edge cases? |
| Code Clarity | Are function names self-explanatory? Is logic easy to follow without comments? |
| DRY Principle | Is there duplicated logic that Copilot can refactor into a shared function? |
| Dependency Safety | Does Copilot flag any known-vulnerable package versions? |

Fix blockers the user agrees to, then update `code-review.md`. Do not open a pull request in this step.
