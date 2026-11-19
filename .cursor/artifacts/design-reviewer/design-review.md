# Design review — KAN-3

**Story:** KAN-3, Show holds that have waited past the pickup window
**Reviewed:** `.cursor/artifacts/requirements-agent/requirements.md` (approved) and `.cursor/artifacts/architect/architecture.md` (approved, 12 assumptions accepted)
**Also read:** `src/holdshelf/server.py`, `src/holdshelf/catalog.py`, `src/holdshelf/static/index.html`, `tests/test_holdshelf.py`, `README.md` (Python 3.9 or newer)
**Pass:** decisions agreed and applied to `.cursor/artifacts/architect/architecture.md`. `requirements.md` was not edited.

## Verdict

The architecture is sound and fits the existing app. It keeps `GET /api/holds` and the pickup action intact, keeps all window rules in one parser, injects "today" for repeatable tests, and adds no secret handling. There are no blockers. The user agreed to every finding below, and those decisions are now in the architecture.

## Findings

| ID | Severity | Area | Short title |
| --- | --- | --- | --- |
| DR-1 | should-fix | Failure path | Page must always send `windowDays`, even when the input is blank |
| DR-2 | should-fix | Failure path | Very long digit strings can crash the request instead of returning 400 |
| DR-3 | should-fix | Validation | The digit check must be a full match, not `^...$` |
| DR-4 | should-fix | Failure path | Page behavior on network error, non-JSON, or other non-200 responses is not defined |
| DR-5 | should-fix | Failure path | Refresh after pickup must reuse the applied window, not the current input |
| DR-6 | should-fix | Tests | No test matrix for the `Not Found` and edge cases, and no check of the page behavior |
| DR-7 | should-fix | Boundaries | Window parser location and sort ownership are left open |
| DR-8 | note | Failure path | Unparseable `readySince` handling depends on the Python version |
| DR-9 | note | Failure path | Unexpected exceptions in `handle` drop the connection and print a traceback |
| DR-10 | note | Secrets | Echoing the rejected `windowDays` in the 400 message |
| DR-11 | note | Existing behavior | `GET /api/holds` must ignore `windowDays` and keep its output |
| DR-12 | note | Validation | Misspelled parameter names fall back to 7 |
| DR-13 | note | Consistency | `requirements.md` still marks zero, negative, and decimal as "Confirm" |
| DR-14 | note | Verification | Live server uses the real date, not 18 November 2026 |
| DR-15 | note | Page | Two quick clicks can render an older response over a newer one |
| DR-16 | note | Compatibility | `ShelfApp` constructor and `Hold` field order must stay compatible |

### DR-1 — Page must always send `windowDays`, even when the input is blank (should-fix)

**Risk.** With `<input type="number">` (Assumption 8), browsers return `value === ""` when the librarian types text that is not a number, such as `abc` or `7days`. If the page builds the URL only when the value is non-empty, or drops an empty parameter, the server sees an omitted `windowDays`, applies 7, and returns a list. That is the guessed list FR-10 and NFR-2 forbid.

**Recommended decision.** The page always sends `?windowDays=<encodeURIComponent(input.value)>`, including `windowDays=` when the value is empty, so the server returns 400. The page never omits the parameter and never substitutes 7 itself.

**Agreed.** The page always sends `windowDays`, even when the input is blank, so a blank or non-numeric input returns 400 instead of falling back to 7.

### DR-2 — Very long digit strings can crash the request instead of returning 400 (should-fix)

**Risk.** Assumption 5 accepts any positive whole number with no upper bound. Python versions with the integer string conversion limit (3.11, and security releases of 3.9 and 3.10) raise `ValueError` from `int()` on strings longer than 4300 digits. The request line can be up to about 64 KB, so `windowDays=999...9` can reach that limit. The parser does not plan to catch it, so `handle` raises, the handler writes no response, and the librarian gets a dropped connection instead of a clear 400.

**Recommended decision.** Revisit Assumption 5. Either:
- (a) Set an upper bound, for example `windowDays` at most 3650 days (10 years), and return 400 above it. This also gives a clear error for a mistyped huge value. Or
- (b) Keep no bound on the value but reject strings longer than a fixed number of digits (for example 6) with 400, and catch `ValueError` from `int()` as a bad window.

The reviewer recommends (a). In both cases the rule lives in `parse_window_days` and is tested.

**Agreed.** Option (a). A valid window is a whole number from 1 to 3650. A value above 3650 returns 400. This replaces Assumption 5's "no upper bound". Leading zeros such as `07` are still accepted as 7 when the numeric value is in range. `00` is 0 and returns 400. A digit string that `int()` cannot convert is a bad window and returns 400.

### DR-3 — The digit check must be a full match, not `^...$` (should-fix)

**Risk.** The architecture says the value must be "ASCII digits only (`[0-9]+`)". In Python, `re.match(r"^[0-9]+$", s)` also accepts a trailing newline, so `windowDays=7%0A` would pass as `"7\n"`. Using `\d` instead of `[0-9]` accepts non-ASCII digits unless `re.ASCII` is set.

**Recommended decision.** Use `re.fullmatch(r"[0-9]+", value)` (or `str.isascii() and str.isdigit()`), then convert, then require the result to be greater than 0. Add tests for `7%0A`, `%207`, `%2B7`, `+7` (which `parse_qs` decodes to `" 7"`), `00`, and `07`.

**Agreed.** The digit check uses `re.fullmatch(r"[0-9]+")`, then requires a value from 1 to 3650. Tests cover `+7`, a leading space (`%207`), a trailing newline (`7%0A`), `00`, and `07`.

### DR-4 — Page behavior on network error, non-JSON, or other non-200 responses is not defined (should-fix)

**Risk.** The architecture defines the page for 200 and 400 only. A rejected `fetch` (server stopped), a non-JSON body, or a 404 or 500 would leave an unhandled promise rejection and possibly an old long-waiting table on screen, shown as if current.

**Recommended decision.** For any outcome other than 200 with a `holds` array, the page clears the long-waiting table and shows a readable message in the long-waiting message area: the server `error` text when present, otherwise "Could not load long-waiting holds." A rejected fetch shows "API unreachable", matching the existing page. The existing list and its message area are not touched.

**Agreed.** If the long-waiting request is not 200 with a `holds` list (network failure, non-JSON, 404, or 500), the page clears that table and shows the server error text, or "Could not load long-waiting holds.", or "API unreachable" when the server cannot be reached. The existing list stays untouched.

### DR-5 — Refresh after pickup must reuse the applied window, not the current input (should-fix)

**Risk.** Assumption 10 reloads the long-waiting view "with the window it is already using". If the librarian edited the input after the last load, reading the input again could send a different or invalid value, and a pickup in the main list would then show a 400 or a different list in the long-waiting section without the librarian asking for it.

**Recommended decision.** The page keeps the `windowDays` from the last successful response (the echoed value in the envelope) and uses that value for the refresh after pickup. If no long-waiting view has loaded successfully, a pickup does not call the overdue endpoint. A failed pickup does not refresh the long-waiting view.

**Agreed.** After a successful pickup, refresh the long-waiting view with the window from the last successful long-waiting response, not the current input. Skip the refresh if that view has never loaded, or if the pickup failed.

### DR-6 — No test matrix for the `Not Found` and edge cases, and no check of the page behavior (should-fix)

**Risk.** The architecture says tests inject a catalog and a fixed date, but it does not list the cases. The page rules (`Not Found` for a `null` phone, the empty-list message, clearing the table on 400) have no automated check. The existing page test only looks for strings.

**Recommended decision.** Add a test matrix to the architecture, with the fixed date 18 November 2026:

| Case | Expected |
| --- | --- |
| Omitted `windowDays` | 200, `windowDays` 7, H-1042 with `daysWaiting` 16 and phone `555-0142` |
| `windowDays=7` | Same as omitted |
| Ready since 11 November, window 7 | Excluded (exactly 7) |
| H-1048 at window 1 | Included, `daysWaiting` 2, `phone` JSON `null` |
| H-1048 at window 2 | Excluded |
| Picked-up hold older than the window | Excluded for every window |
| Ready hold with `ready_since` `None`, empty, or unparseable | Excluded for every window, no error |
| Ready hold with a future `readySince` | Excluded, no error |
| No hold matches | 200, `holds` is `[]` |
| `abc`, `7days`, empty, `?windowDays` with no `=`, `0`, `00`, `-1`, `7.5`, `7.0`, `+7`, `%207`, `7%0A`, repeated parameter, value above the bound from DR-2 | 400, `error` present, no `holds` key |
| `GET /api/holds?windowDays=abc` | 200, unchanged full list |
| Existing pickup tests | Still pass (404 unknown id, 409 second pickup) |

For the page, keep the unittest string checks (the page references `/api/holds/overdue` and contains `Not Found` and the empty-list message), and have the verifier in Step 7 exercise the page in a browser for a `null` phone, an empty list, a 400, and refresh after pickup.

**Agreed.** The test matrix is in the architecture, with the fixed date 18 November 2026. It covers exact-window, null phone, missing or unparseable or future `readySince`, picked-up, empty list, the bad-window values, and unchanged `GET /api/holds`. The Step 7 browser check covers a `Not Found` phone, the empty message, a 400 display, and refresh after pickup, using the actual run date.

### DR-7 — Window parser location and sort ownership are left open (should-fix)

**Risk.** The window parser is placed in "`server.py` (or a small new module `holdshelf/window.py`)". The sort order (Assumption 3) has no owner. Leaving both open makes the plan and code review harder, and the sort could end up split between the route and the catalog.

**Recommended decision.** Put `parse_window_days` and `BadWindowError` in `server.py`, next to the only route that uses them, which keeps the change small. `Catalog.list_overdue` owns filtering, the `daysWaiting` count, and the sort, so the route only parses, calls, and wraps the result.

**Agreed.** `parse_window_days` and `BadWindowError` live in `server.py`. `Catalog.list_overdue` owns the filter, the `daysWaiting` count, and the sort. The route only parses, calls, and wraps the result.

### DR-8 — Unparseable `readySince` handling depends on the Python version (note)

`date.fromisoformat` accepts only `YYYY-MM-DD` on Python 3.9 and 3.10, but on 3.11 and later it also accepts forms such as `20261102` and ISO week dates. README requires Python 3.9 or newer. `list_overdue` must catch `ValueError` and `TypeError` and skip the hold (Assumption 4). **Recommended decision:** accept the version difference, because the seed uses `YYYY-MM-DD` and only that format is tested. Optionally require a strict `YYYY-MM-DD` match before parsing, so behavior is the same on every version.

**Agreed.** Accept the Python version difference in `date.fromisoformat`. The seed and the tests use `YYYY-MM-DD`. `list_overdue` still catches `ValueError` and `TypeError` and skips the hold. Do not add a strict pre-parse regex.

### DR-9 — Unexpected exceptions in `handle` drop the connection and print a traceback (note)

The current server has no catch-all. An unexpected exception makes `socketserver` print a traceback to stderr and close the connection with no response. The traceback can contain a `readySince` value but no phone. This is existing behavior and outside the story. **Recommended decision:** do not add a catch-all in this story. DR-2 and DR-8 remove the known causes in the new route.

**Agreed.** Do not add a catch-all for unexpected exceptions in this story.

### DR-10 — Echoing the rejected `windowDays` in the 400 message (note)

The architecture allows the 400 message to repeat the rejected value. It holds no patron data and is safe with `json.dumps` and `textContent`, but it can be up to about 64 KB of reflected input. **Recommended decision:** either do not echo the value ("windowDays must be a whole number of days from 1 to 3650."), or echo it only when it is short (for example 20 characters or fewer). The reviewer prefers not echoing it.

**Agreed.** The 400 message does not echo the rejected value. The wording is `windowDays must be a whole number of days from 1 to 3650.`

### DR-11 — `GET /api/holds` must ignore `windowDays` and keep its output (note)

The routing change parses the query string. Only the overdue route reads `windowDays`. `GET /api/holds?windowDays=abc` must still return 200 with the full list, and `to_dict` must keep the same keys and order. Covered by the matrix in DR-6. **Recommended decision:** confirm as stated.

**Agreed.** `GET /api/holds` ignores `windowDays` and keeps its current output.

### DR-12 — Misspelled parameter names fall back to 7 (note)

`?windowdays=abc` or `?window=3` is not `windowDays`, so the server treats the window as omitted and returns the 7-day list. This matches FR-4 ("omitted means 7"). The page always sends the correct name. **Recommended decision:** accept. Unknown parameters are ignored, and the echoed `windowDays: 7` in the response makes the applied window visible.

**Agreed.** A misspelled parameter name is treated as omitted and uses 7. Unknown parameters are ignored. The response includes the applied `windowDays` so the applied window is visible.

### DR-13 — `requirements.md` still marks zero, negative, and decimal as "Confirm" (note)

The user confirmed that zero, negative, and decimal values return 400, and the architecture records this. `requirements.md` still has the "Confirm" section and "subject to the Confirm item above" in FR-10 and AC-9. **Recommended decision:** the orchestrator asks the requirements agent to record the confirmation in `requirements.md` without changing IDs, so the verifier reads one consistent rule.

**Agreed.** Zero, negative, and decimal `windowDays` values return 400. That confirmation is recorded in this review and in the architecture. `requirements.md` was not edited on this pass and still has the Confirm wording. The requirements agent owns that file.

### DR-14 — Live server uses the real date, not 18 November 2026 (note)

The seed describes the shelf on 18 November 2026, but the live server uses `date.today()`. On any later date the day counts and the list differ from AC-1 (for example, H-1102 becomes overdue at window 7 once it has waited 8 days). **Recommended decision:** acceptance criteria are proven by unit tests with the injected date. The Step 7 browser check compares the page against the expected counts for the actual run date, and the verification report states that date.

**Agreed.** Acceptance criteria are proven by unit tests with the injected date 18 November 2026. The Step 7 browser check compares the page against the expected counts for the actual run date, and the verification report states that date.

### DR-15 — Two quick clicks can render an older response over a newer one (note)

If the librarian clicks "Show long-waiting holds" twice with different windows, the first response can arrive last and overwrite the second. **Recommended decision:** disable the button while a request is in flight, as the existing pickup button does, or ignore responses that are not the latest request.

**Agreed.** Disable the long-waiting button while a request is in flight, the same way the existing pickup button works.

### DR-16 — `ShelfApp` constructor and `Hold` field order must stay compatible (note)

`serve()` and the tests call `ShelfApp(catalog)` positionally, and tests build `Hold(...)` with positional fields. **Recommended decision:** add `today` as an optional keyword argument after `catalog`, and change only the type of `Hold.ready_since` to `str | None` without moving it or giving it a default.

**Agreed.** Add `today` as an optional keyword argument after `catalog` on `ShelfApp`. Change only the type of `Hold.ready_since` to `str | None`, without moving the field or giving it a default.

## Scope check

No finding adds scope beyond the requirements. The architecture's extras (echoing `windowDays`, rejecting a repeated parameter, refreshing after pickup, sort order) were accepted by the user as assumptions. Nothing in the design sends email or SMS, calls an external system, or changes how pickup works.

## Secrets check

The hold shelf server reads no tokens, `.env`, or `config/jira.local.json`, and the design adds none. There is no access log, and no new logging. Phone numbers appear only in the JSON body and the page. The 400 message does not repeat the rejected window (DR-10).

## Decisions

The user agreed to DR-1 through DR-16. Each finding above records that decision, and the same decisions are in `.cursor/artifacts/architect/architecture.md`. Assumption 5 now has the range 1 to 3650. Assumptions 8, 10, and 11 were revised to match DR-1, DR-5, DR-15, and DR-16.

`requirements.md` was not edited. It still has the Confirm wording for zero, negative, and decimal `windowDays` values (FR-10, AC-9, and the Confirm section). The user has confirmed those values return 400. The requirements agent owns that file.
