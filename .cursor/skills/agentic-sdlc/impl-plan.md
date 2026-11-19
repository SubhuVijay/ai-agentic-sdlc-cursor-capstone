# Step 4 — Implementation plan

Prerequisite: `.cursor/artifacts/design-reviewer/design-review.md`, and `.cursor/artifacts/architect/architecture.md` already includes the agreed review decisions.

Create `.cursor/artifacts/planner/` if needed and write `.cursor/artifacts/planner/impl-plan.md` from the approved architecture. Do not write it at the repository root.

- Order tasks by dependency (`T1`, `T2`, ...).
- For each task record the outcome, the files it will touch, what it depends on, and the definition of done.
- Add a blocked list: tasks that cannot start until another task finishes.
- Name the first task that is free to start.

Wait for the user to approve the plan and to name which task to implement.
