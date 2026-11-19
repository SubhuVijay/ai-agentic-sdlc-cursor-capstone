# Step 7 — Verify

Prerequisite: `.cursor/artifacts/code-reviewer/code-review.md` has no open blocker the user still wants fixed.

1. Run the full test suite with `python -m unittest discover -s tests -v`. Record the command and the full output. Hook, story-loader, and hold-shelf tests are in the same run.
2. Check the hold shelf against `.cursor/artifacts/requirements-agent/requirements.md`:
   - The existing list and pickup action still behave as they do now.
   - The long-waiting view and `GET /api/holds/overdue` match the approved rules.
   - A missing phone is the text `Not Found` where the requirements require it.
   - Secrets, tokens, and `.env` values are absent.
3. Create `.cursor/artifacts/verifier/` if needed and write `.cursor/artifacts/verifier/verification-report.md` with the command, the pass or fail result, and any content-quality failures. Do not write it at the repository root.
4. Fix in-scope failures, re-run, and replace the recorded output. Ask the user before widening the fix past the approved tasks.
