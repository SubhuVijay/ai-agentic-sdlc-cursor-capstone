# Step 3 — Design review

Prerequisite: `.cursor/artifacts/architect/architecture.md`.

Review `.cursor/artifacts/requirements-agent/requirements.md` and `.cursor/artifacts/architect/architecture.md` as a senior reviewer. Do not write production code.

1. Identify risks and gaps: missing failure paths, secret leakage, unclear component boundaries, untested `Not Found` cases, changes that would break the existing list or pickup action, and scope that the requirements do not include.
2. Give each finding a severity of blocker, should-fix, or note, plus a recommended decision.
3. Create `.cursor/artifacts/design-reviewer/` if needed and write `.cursor/artifacts/design-reviewer/design-review.md` with the findings. Do not write it at the repository root. Record a decision only after the user agrees to it.
4. Update `.cursor/artifacts/architect/architecture.md` for every agreed change.
5. Stop. Implementation starts at Step 5, after the plan is approved.
