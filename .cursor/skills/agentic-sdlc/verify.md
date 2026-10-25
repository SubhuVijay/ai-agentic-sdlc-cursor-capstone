# Step 7 — Verify

Prerequisite: `code-review.md` has no open blocker the user still wants fixed.

1. Run the full test suite. Record the command and the full output.
2. Check the generated documentation snapshot against `requirements.md`:
   - Required sections are present.
   - A fact that cannot be determined is the text `Not Found`.
   - Secrets, tokens, and `.env` values are absent.
3. Write `verification-report.md` with the command, the pass or fail result, and any content-quality failures.
4. Fix in-scope failures, re-run, and replace the recorded output. Ask the user before widening the fix past the approved tasks.
