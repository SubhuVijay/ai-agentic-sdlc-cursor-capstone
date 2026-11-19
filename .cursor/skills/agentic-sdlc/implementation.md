# Step 5 — Implementation

Prerequisite: the user approved `.cursor/artifacts/planner/impl-plan.md` and named the task to build.

1. Implement that task only.
2. Follow `.cursor/artifacts/requirements-agent/requirements.md`, `.cursor/artifacts/architect/architecture.md`, and the decisions in `.cursor/artifacts/design-reviewer/design-review.md`.
3. Extend `src/holdshelf` and put tests in `tests/`. Do not replace the existing list or pickup action. Do not write a markdown artifact at the repository root.
4. Validate user input. Keep secrets out of output and logs. Write `Not Found` when the story says a missing phone or date cannot be determined.
5. Handle a bad window value, a missing hold, and an empty overdue list with a readable result, not an uncaught stack trace.
6. Add tests for the happy path and for the missing-field / `Not Found` cases this task introduces.
7. When the task's definition of done is met, summarize the files changed and wait before the next task.
