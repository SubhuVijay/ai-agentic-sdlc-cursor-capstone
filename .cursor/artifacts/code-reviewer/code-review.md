# Code review — KAN-3

**Story:** KAN-3, Show holds that have waited past the pickup window
**Pass:** first review, then a second pass to record the user's decisions. No product code changed on either pass.
**Scope:** T1 to T4 from `.cursor/artifacts/planner/impl-plan.md`
- `src/holdshelf/catalog.py` (T1)
- `src/holdshelf/server.py` (T2, T3)
- `src/holdshelf/static/index.html` (T4)
- `tests/test_holdshelf.py`

**Judged against:** `.cursor/artifacts/requirements-agent/requirements.md`, `.cursor/artifacts/architect/architecture.md`, `.cursor/artifacts/design-reviewer/design-review.md` (DR-1 to DR-16), `.cursor/artifacts/planner/impl-plan.md`.

## Summary

| Area | Result | Severity of open items |
| --- | --- | --- |
| Correctness | pass | — |
| Security | pass | note |
| Error Handling | pass | note |
| Test Coverage | pass | note |
| Code Clarity | pass | note |
| DRY Principle | pass | DRY-1 deferred by the user; no code change |
| Dependency Safety | pass | — |

No blockers. The user has decided every open item: DRY-1 is deferred, EH-2, TC-2, CL-1, CL-2, and CL-3 stay as notes, and SEC-1, EH-1, and DRY-2 stay out of scope. No product code was changed, so the review is accepted as written.

**Test run.** The shell in this review session returned no exit status for `python -m unittest tests.test_holdshelf`, so this review did not reproduce the result. The implementer reported 44 tests passing. The test file contains 44 test methods (7 + 12 + 9 + 16 across the four classes), which is consistent with that report. Step 7 (verifier) must run the suite and record the result.

---

## Correctness — pass

**Question:** Does each component behave as specified in the requirements?

| Requirement | Where it is met | Evidence |
| --- | --- | --- |
| FR-2, FR-5, AC-3 strictly longer wait | `Catalog.list_overdue`, `days_waiting > window_days` (`catalog.py`) | `test_exact_seven_days_is_excluded`, `test_exact_seven_day_wait_is_excluded` |
| FR-8, AC-5 picked-up excluded | `if hold.status != "ready": continue` | `test_picked_up_hold_is_excluded` (catalog and route) |
| FR-8, AC-4 missing `readySince` excluded | `None` / `""` skip and `fromisoformat` `ValueError`/`TypeError` skip (DR-8) | `test_missing_or_unparseable_ready_since_is_excluded`, `test_missing_ready_since_is_excluded` |
| FR-6 existing fields plus days | `self.to_dict(hold)` plus `daysWaiting` | `test_result_keys` |
| NFR-3 phone stays JSON `null` | `to_dict` passes `phone` through | `test_h1048_is_included_at_window_1_with_a_null_phone`, `test_window_1_includes_the_hold_with_no_phone` |
| AC-1 seed at 18 Nov 2026 | Only H-1042, 16 days, Maya Chen, `555-0142` | `test_seed_window_7_returns_only_the_sixteen_day_hold`, `test_omitted_window_returns_the_sixteen_day_hold` |
| AC-2 H-1048 at windows 7 and 2 | Excluded | `test_h1048_is_excluded_at_window_2`, `test_window_2_excludes_h1048` |
| FR-4, NFR-2 omitted window is 7 | `parse_window_days(None or [])` returns 7 | `test_omitted_window_defaults_to_seven` |
| FR-10, AC-8, AC-9, AC-12, decisions 7/9/10 | `re.fullmatch(r"[0-9]+")`, `int()`, range 1 to 3650, fixed message | `WindowParserTests`, `test_bad_windows_return_the_fixed_error` |
| NFR-1 server-local today | `ShelfApp.today` defaults to `date.today` and is injectable | `test_today_defaults_to_the_server_date` |
| FR-11, AC-10 existing routes unchanged | `GET /api/holds` and pickup branches untouched; `/api/holds?windowDays=abc` ignored (DR-11) | `test_hold_list_ignores_the_window_query`, `test_pickup_still_reports_unknown_and_repeat_pickup` |
| FR-3, FR-7, FR-9, AC-6, AC-7, AC-11 page | New section in `index.html`: input starts at 7, `Not Found` for `null` phone, empty message, existing list keeps its five columns plus action | `test_page_includes_the_long_waiting_section` (string checks); behavior in a browser is Step 7 |
| DR-1 always send `windowDays` | `"/api/holds/overdue?windowDays=" + encodeURIComponent(windowValue)` | page string check |
| DR-5 refresh after pickup uses applied window | `rememberedWindowDays = payload.windowDays`, reused in `pickup()` only after success | inspection of `index.html` |
| DR-15 no stale overwrite | Button disabled in `try`/`finally` around the request | inspection of `index.html` |

The Not Found items in the requirements (days field name, envelope, sort order) were settled in the architecture as `daysWaiting`, `{"windowDays", "holds"}`, and longest wait first then `id`. The code matches those choices (`test_sorts_longest_wait_first_then_id`).

## Security — pass

**Question:** Are secrets excluded from output? Is user input validated?

- **Secrets.** No new `print`, logging, or environment reads. `log_message` still returns without writing (`server.py`). No phone or hold data in `console.log` (`test_page_includes_the_long_waiting_section` asserts `console.log` is absent).
- **Input validation.** `windowDays` is validated by a single function with a full-match ASCII digit check, an `int()` guard for very long strings (DR-2), and a 1 to 3650 range (`parse_window_days`, `server.py`). Signs, spaces, newlines, non-ASCII digits, and repeated parameters are rejected (`test_signs_spaces_newlines_and_non_ascii_digits_are_rejected`, `test_repeated_window_is_rejected`).
- **No reflection.** The 400 body is the fixed `BAD_WINDOW_MESSAGE` and never repeats the rejected value (DR-10). Tests assert the encoded body does not contain the input (`test_bad_windows_return_the_fixed_error`).
- **Output encoding.** The page writes every value with `textContent`, so hold data cannot inject markup (`index.html`, `render` and `renderLongWaiting`).

**Note SEC-1 (note, existing behavior; out of scope for this story by user decision; no code change).** The pickup 404 and 409 messages repeat the hold id from the URL (`server.py`, `_pickup`). This predates the story, is JSON-encoded, and is shown with `textContent`, so it is not an injection risk. Out of scope for KAN-3.

## Error Handling — pass

**Question:** Are bad input, a missing hold, and an empty overdue list handled gracefully?

- **Bad input.** Every bad `windowDays` returns 400 with the fixed message and no `holds` key (`test_bad_windows_return_the_fixed_error`). The page clears the long-waiting table and shows the server error text (`showLongWaitingProblem` in `index.html`).
- **Missing hold.** Unknown pickup id still returns 404 and does not change the shelf (`test_unknown_hold_returns_404`, `test_pickup_still_reports_unknown_and_repeat_pickup`). A hold with a missing or unparseable `readySince` is skipped without an exception (`test_missing_or_unparseable_ready_since_is_excluded`). `POST /api/holds/overdue` falls through to 404 (`test_post_overdue_is_not_the_overdue_view`).
- **Empty overdue list.** Returns 200 with `holds: []` (`test_window_3650_returns_an_empty_list`). The page shows "No ready hold is past the pickup window." (`renderLongWaiting`).
- **Page failures (DR-4).** `loadLongWaiting` handles a rejected `fetch` ("API unreachable"), a non-JSON body ("Could not load long-waiting holds."), and any non-200 with an `error` field. It does not touch the existing list's message area.

**Note EH-1 (note, existing behavior; out of scope for this story by user decision; no code change).** The existing `pickup()` function does not catch a rejected `fetch` or a non-JSON body, so a network failure during pickup leaves the button disabled with no message (`index.html`, `pickup`). This predates the story and the plan said to leave the pickup flow as it is.

**Note EH-2 (note; kept as a note by user decision; not applied).** The window input has `min="1"` but no `max="3650"` (`index.html`). The server still rejects 3651 with a readable message, so behavior is correct; adding `max` would only give earlier browser feedback.

## Test Coverage — pass

**Question:** Do tests cover the happy path AND the Not Found / missing-field edge cases?

- **Happy path.** Seed list at the default and explicit window 7 (`test_omitted_window_returns_the_sixteen_day_hold`, `test_window_7_and_07_match_the_omitted_window`), sort order, result keys.
- **Not Found phone.** `phone` is `None` in the catalog and in the route at window 1 (`test_h1048_is_included_at_window_1_with_a_null_phone`, `test_window_1_includes_the_hold_with_no_phone`). The page contains the `Not Found` display string.
- **Missing field.** `ready_since` of `None`, `""`, and `"not-a-date"` (`test_missing_or_unparseable_ready_since_is_excluded`), `Hold` construction with `None` (`test_hold_accepts_a_missing_ready_since`), and `list_holds` keeping a `None` `readySince` (`test_list_holds_keeps_a_missing_ready_since`).
- **Boundaries.** Exact window, future date, 1 and 3650 accepted, 0 and 3651 rejected, 5000-digit string.
- **Every bad-window case in AC-8, AC-9, AC-12 and the DR-6 matrix** is in `test_bad_windows_return_the_fixed_error`.
- **Regression.** The original tests are unchanged and still present.

**Note TC-1 (note).** Page tests are string checks only. Click handling, button disabling, `Not Found` rendering, the empty message, and refresh after pickup are not exercised by a test. The plan assigns this to the Step 7 browser check.

**Note TC-2 (note; kept as a note by user decision; not applied).** `test_today_defaults_to_the_server_date` compares `app.today()` with `date.today()` in two calls and could fail if the test runs across midnight. The identity assertions above it already prove the default; the equality line could be dropped.

## Code Clarity — pass

**Question:** Are function names self-explanatory? Is logic easy to follow without comments?

- Names state the fact or failure: `list_overdue`, `parse_window_days`, `BadWindowError`, `BAD_WINDOW_MESSAGE`, `renderLongWaiting`, `showLongWaitingProblem`, `rememberedWindowDays`.
- `list_overdue` reads top to bottom as the rules in FR-5 and FR-8. `parse_window_days` reads as the rule list in decision 9.
- The overdue route in `handle` is short and returns either 400 or 200 with no hidden branches.

**Note CL-1 (note; kept as a note by user decision; not applied).** In `list_overdue`, `if hold.ready_since is None or hold.ready_since == "":` could be `if not hold.ready_since:` with the same behavior.

**Note CL-2 (note; kept as a note by user decision; not applied).** The `try`/`except ValueError` around `int(value)` in `parse_window_days` only exists for Python's integer-string length limit (DR-2). That is not obvious from the code alone; a one-line comment stating that constraint would help the next reader.

**Note CL-3 (note; kept as a note by user decision; not applied).** The overdue branch in `handle` calls `urlparse(target)` a second time; the top of `handle` already parses it for `path`. Keeping the parsed result in one variable would read slightly cleaner.

## DRY Principle — pass (DRY-1 deferred by the user)

**Question:** Is there duplicated logic that could be refactored into a shared function?

**DRY-1 (deferred by the user; recorded as a note, not an open fix).** `src/holdshelf/static/index.html` builds table rows twice with the same code:
- `render` and `renderLongWaiting` each build an "empty" row the same way (`tr`, one `td` with `colSpan = 6`, class `empty`, `textContent`), differing only in the target `tbody` and the text.
- Both loop over a value array creating one `td` per value with `textContent`.

The implementation rule says to share duplicated logic rather than copy the same check into a second function. Two small helpers (for example `appendEmptyRow(tbody, text)` and `appendCells(row, values)`) would remove the copy. This touches the existing `render` function, which the plan asked to leave as it is, 

**Decision (user):** deferred. Do not extract a shared row helper now. The existing `render` function stays as it is, and `renderLongWaiting` keeps its own copy of the row code. No product code was changed.

**Note DRY-2 (note, existing behavior; out of scope for this story by user decision; no code change).** The status literals `"ready"` and `"picked-up"` appear in several places in `catalog.py` (`list_overdue`, `mark_picked_up`, seed data). This predates the story; named constants would be a small follow-up.

Server side is not duplicated: the window rule lives only in `parse_window_days`, the message only in `BAD_WINDOW_MESSAGE`, and the overdue rows reuse `Catalog.to_dict`.

## Dependency Safety — pass

**Question:** Are any known-vulnerable package versions in use?

- No third-party packages. `server.py` states "The standard library is the only dependency," and the imports in `catalog.py`, `server.py`, and `tests/test_holdshelf.py` are standard library only (`dataclasses`, `datetime`, `http.server`, `json`, `pathlib`, `re`, `typing`, `urllib.parse`, `unittest`, `sys`).
- No `requirements*.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, or `package.json` exists in the repository.
- The page loads no external scripts or stylesheets (`index.html`).
- Python interpreter version in use: Not Found (the shell did not return output in this session).

## Decisions recorded

1. **DRY-1: deferred by the user.** No shared row helper is extracted. The existing `render` function stays as it is. The duplication is a recorded note, not an open fix. No code change was made.
2. **EH-2, TC-2, CL-1, CL-2, CL-3: stay as notes.** None of them is applied (no `max="3650"` on the input, no change to the midnight-sensitive assertion, no further edits to `catalog.py` or `server.py`). No code change was made.
3. **SEC-1, EH-1, DRY-2: out of scope for this story.** They concern code that predates KAN-3 and are left as they are. No code change was made.

Result: the review is accepted with no code changes. No area is marked fix. Verification (Step 7) is the next step, and it must run the test suite because this review did not reproduce the test result.
