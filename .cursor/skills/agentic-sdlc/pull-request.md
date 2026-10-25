# Step 8 — Pull request

Prerequisite: `verification-report.md` records a passing run, and the user asked to open the pull request.

1. Add an `## [Unreleased]` entry to `CHANGELOG.md` for the product changes since `0.1.0`.
2. Use `.github/PULL_REQUEST_TEMPLATE.md`. The description must contain every section below:
   - Summary — 2-3 sentence overview of what was built and why.
   - Changes Made — bulleted list of all files added/modified and the reason.
   - Test Evidence — paste the test run output or link to CI results.
   - Known Limitations — anything marked 'Not Found' or out of scope.
   - Reviewer Checklist — a tick-list the reviewer must complete before approving.
3. Fill Test Evidence from `verification-report.md` or from CI on the branch.
4. Fill Known Limitations from requirements that are out of scope and from snapshot fields whose value is `Not Found`.
5. Leave the Reviewer Checklist unticked. The reviewer completes it.
6. Push and open the pull request only after the user confirms the remote and the base branch.
