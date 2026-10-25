# Step 3 — Design review

Prerequisite: `architecture.md`.

Review `requirements.md` and `architecture.md` as a senior reviewer. Do not write production code.

1. Identify risks and gaps: missing failure paths, secret leakage, unclear component boundaries, untested `Not Found` cases, and scope that the requirements do not include.
2. Give each finding a severity of blocker, should-fix, or note, plus a recommended decision.
3. Write `design-review.md` with the findings. Record a decision only after the user agrees to it.
4. Update `architecture.md` for every agreed change.
5. Stop. Implementation starts at Step 4, after the plan is approved.
