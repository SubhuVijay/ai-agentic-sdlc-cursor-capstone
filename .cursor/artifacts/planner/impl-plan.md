# Implementation plan — KAN-3

**Story:** KAN-3, Show holds that have waited past the pickup window
**Inputs (approved):**
- `.cursor/artifacts/requirements-agent/requirements.md`
- `.cursor/artifacts/architect/architecture.md` (includes DR-1 to DR-16)
- `.cursor/artifacts/design-reviewer/design-review.md`

**Extends:** `src/holdshelf/catalog.py`, `src/holdshelf/server.py`, `src/holdshelf/static/index.html`, `tests/test_holdshelf.py`

## Ground rules for every task

- Extend `src/holdshelf`. Do not replace `GET /api/holds`, the pickup route, or the existing list and pickup button on the page (FR-11, AC-10, AC-11).
- Python standard library only. Keep Python 3.9 compatibility (README). `from __future__ import annotations` is already at the top of both modules, so `str | None` in annotations is fine.
- Tests use `unittest` and live in `tests/test_holdshelf.py`, next to the existing tests. They call `Catalog` or `ShelfApp.handle` directly and do not open a socket. The fixed date is `date(2026, 11, 18)` (DR-6, DR-14).
- No new `print` or `logging` calls. No catch-all `except Exception` in `handle` (DR-9). Phone numbers never appear in error messages.
- The existing six tests in `tests/test_holdshelf.py` must keep passing after every task.
- Run with `python -m unittest discover -s tests` (or `python -m unittest tests.test_holdshelf`).

## Task order

| Task | Outcome | Depends on | Free to start |
| --- | --- | --- | --- |
| T1 | `Catalog.list_overdue` and `Hold.ready_since: str \| None` | none | yes |
| T2 | `parse_window_days` and `BadWindowError` in `server.py` | none | yes |
| T3 | `GET /api/holds/overdue` route and injectable `today` on `ShelfApp` | T1, T2 | no |
| T4 | "Long-waiting holds" section on the page | T3 | no |

T1 and T2 do not depend on each other. Both edit `tests/test_holdshelf.py`, so implement them one at a time, not in parallel.

---

## T1 — Overdue query in the catalog

**Outcome.** `Catalog` can return the ready holds that have waited strictly longer than a given window on a given date, each with `daysWaiting`, sorted longest wait first. A hold may have no `readySince`.

**Files.**
- `src/holdshelf/catalog.py`
- `tests/test_holdshelf.py`

**Depends on.** None.

**Work.**
1. Change only the annotation of `Hold.ready_since` from `str` to `str | None`. Keep it the fourth field, after `patron` and before `status`, with no default (DR-16). Leave `seed_holds()`, `list_holds()`, `mark_picked_up()`, and `to_dict()` keys and order unchanged.
2. Add `Catalog.list_overdue(self, window_days: int, today: date) -> list[dict]` (DR-7, DR-8):
   - Keep only holds with `status == "ready"`.
   - Skip a hold whose `ready_since` is `None` or empty.
   - Parse with `date.fromisoformat(hold.ready_since)`. On `ValueError` or `TypeError`, skip the hold. No pre-parse regex.
   - `days_waiting = (today - ready).days`. Keep the hold only when `days_waiting > window_days` (strictly greater, FR-5, AC-3). A future date gives a negative count and is skipped by the same rule.
   - Each result is `self.to_dict(hold)` plus `"daysWaiting": days_waiting`, so `phone` stays `None` (JSON `null`) (NFR-3).
   - Sort by `daysWaiting` descending, then `id` ascending (Assumption 3).
   - Do not validate `window_days`. The caller passes a checked int.

**Tests (call `Catalog.list_overdue` directly with `today = date(2026, 11, 18)`).**

| Case | Expected |
| --- | --- |
| Seed catalog, window 7 | Only H-1042, `daysWaiting` 16, phone `555-0142` (AC-1). H-1048 (2 days), H-1102 (6 days), and H-0991 (picked up) absent |
| Ready since `2026-11-11`, window 7 | Excluded, waited exactly 7 days (AC-3) |
| H-1048 at window 1 | Included, `daysWaiting` 2, `phone` is `None` (AC-2, AC-6) |
| H-1048 at window 2 | Excluded (AC-2) |
| Picked-up hold older than the window (H-0991) | Excluded at windows 1, 7, and 3650 (AC-5) |
| Ready hold with `ready_since` `None`, `""`, or `"not-a-date"` | Excluded at windows 1 and 7, no exception (AC-4) |
| Ready hold with a future `readySince` (`2026-11-25`) | Excluded, no exception |
| No hold matches (seed at window 3650) | Returns `[]` |
| Sort | Holds with different waits come back longest first. Two holds with the same wait come back in `id` order |
| Result keys | `id`, `title`, `patron`, `readySince`, `status`, `phone`, `daysWaiting` |
| `list_holds()` with a `None` `ready_since` hold | Still returns the hold with `readySince` `None`, keys unchanged |

**Done when.**
- All T1 tests and the six existing tests pass.
- `Hold("X", "T", "P", None, "ready")` constructs without error, and positional construction used by the existing tests is unchanged.
- `server.py` and `index.html` are not touched.

---

## T2 — Window parser in the server module

**Outcome.** One function in `server.py` turns the raw `windowDays` query values into a valid int from 1 to 3650, or raises `BadWindowError` with the fixed message.

**Files.**
- `src/holdshelf/server.py`
- `tests/test_holdshelf.py`

**Depends on.** None.

**Work.**
1. Add `import re` to `server.py`.
2. Add a module constant for the fixed message: `windowDays must be a whole number of days from 1 to 3650.` (NFR-5, DR-10).
3. Add `class BadWindowError(ValueError)` whose message is that fixed text. It never includes the rejected value.
4. Add `parse_window_days(raw: list[str] | None) -> int` (DR-2, DR-3, DR-7, DR-12):
   - `None` or an empty list returns 7 (FR-4, NFR-2).
   - More than one value raises `BadWindowError` (Assumption 6).
   - The single value must satisfy `re.fullmatch(r"[0-9]+", value)`. Otherwise raise.
   - Convert with `int(value)`. A `ValueError` from `int()` raises `BadWindowError`.
   - The integer must be from 1 to 3650 inclusive. Otherwise raise.
5. Do not wire the parser into `handle` yet. That is T3.

**Tests (call `parse_window_days` directly with already-decoded values, as `parse_qs` would deliver them).**

| Input | Expected |
| --- | --- |
| `None`, `[]` | 7 |
| `["7"]` | 7 |
| `["07"]` | 7 |
| `["1"]` | 1 |
| `["3650"]` | 3650 (AC-12) |
| `["abc"]`, `["7days"]`, `[""]` | `BadWindowError` (AC-8) |
| `["0"]`, `["00"]`, `["-1"]`, `["7.5"]`, `["7.0"]` | `BadWindowError` (AC-9) |
| `["+7"]`, `[" 7"]`, `["7\n"]`, a non-ASCII digit such as `["٧"]` | `BadWindowError` (DR-3, Assumption 7) |
| `["7", "9"]` | `BadWindowError` (Assumption 6) |
| `["3651"]` | `BadWindowError` (AC-12) |
| A digit string of 5000 `9`s | `BadWindowError`, not an uncaught exception (DR-2) |
| Message of any `BadWindowError` | Exactly `windowDays must be a whole number of days from 1 to 3650.` and does not contain the rejected value (e.g. not `3651`, not `abc`) (DR-10) |

**Done when.**
- All T2 tests and the six existing tests pass.
- `ShelfApp.handle` behavior is unchanged. `catalog.py` and `index.html` are not touched.

---

## T3 — Overdue route and injectable "today"

**Outcome.** `GET /api/holds/overdue` returns `200 {"windowDays": n, "holds": [...]}` for a valid or omitted window and `400 {"error": "<fixed message>"}` for a bad one. "Today" is injectable for tests and defaults to the server-local date.

**Files.**
- `src/holdshelf/server.py`
- `tests/test_holdshelf.py`

**Depends on.** T1 (`Catalog.list_overdue`), T2 (`parse_window_days`, `BadWindowError`).

**Work.**
1. Change the constructor to `ShelfApp.__init__(self, catalog: Catalog | None = None, *, today: Callable[[], date] | None = None)`. Store `today if today is not None else date.today` (DR-16, NFR-1). `serve()` keeps calling `ShelfApp(catalog)`.
2. Import `date` from `datetime`, `Callable` from `typing`, and `parse_qs` from `urllib.parse`.
3. In `handle`, add an exact match for `method == "GET" and path == "/api/holds/overdue"` before the fallback 404. It must not disturb the pickup route, which needs the `/pickup` suffix and `POST`.
4. In that route only:
   - `query = parse_qs(urlparse(target).query, keep_blank_values=True)` so `windowDays=` reaches the parser as `[""]`.
   - `window = parse_window_days(query.get("windowDays"))`. Only the exact name `windowDays` counts. Other or misspelled names are ignored (DR-12).
   - On `BadWindowError`, return `400, {"error": <fixed message>}` with no `holds` key (FR-10, DR-10).
   - Otherwise return `200, {"windowDays": window, "holds": self.catalog.list_overdue(window, self.today())}`.
5. `GET /api/holds` keeps ignoring the query string (DR-11). No catch-all around `handle` (DR-9). No logging.

**Tests (call `ShelfApp(catalog, today=lambda: date(2026, 11, 18)).handle(...)`; use the seed catalog unless a row says otherwise).**

| Request | Expected |
| --- | --- |
| `GET /api/holds/overdue` | 200, `windowDays` 7, `holds` is only H-1042 with `daysWaiting` 16, patron Maya Chen, phone `555-0142` (AC-1) |
| `?windowDays=7` and `?windowDays=07` | Same list as omitted, `windowDays` 7 |
| `?windowDays=1` | Includes H-1048 with `daysWaiting` 2 and `phone` `None` (AC-6) |
| `?windowDays=2` | H-1048 absent (AC-2) |
| Injected catalog with a hold ready since `2026-11-11`, `?windowDays=7` | That hold absent (AC-3) |
| Injected catalog with a ready hold whose `ready_since` is `None` | Absent, 200 (AC-4) |
| H-0991 (picked up) | Absent at windows 1 and 7 (AC-5) |
| `?windowDays=3650` | 200, `windowDays` 3650, `holds` is `[]` (AC-12, FR-9, AC-7) |
| `?windowDays=abc`, `7days`, `` (empty, `?windowDays=`), `?windowDays` with no `=`, `0`, `00`, `-1`, `7.5`, `7.0`, `%2B7`, `+7`, `%207`, `7%0A`, `?windowDays=7&windowDays=9`, `3651`, and a 5000-digit string | 400, body is exactly `{"error": "windowDays must be a whole number of days from 1 to 3650."}`, no `holds` key, body does not contain the rejected value (AC-8, AC-9, AC-12, DR-3, DR-10) |
| `?windowdays=abc` and `?window=3` | 200, `windowDays` 7 (DR-12) |
| `?windowDays=7&foo=bar` | 200, `windowDays` 7 |
| `GET /api/holds?windowDays=abc` | 200, full list, same keys and order as without the query (DR-11, AC-10) |
| `POST /api/holds/overdue` | Not routed to the overdue view (falls through to the existing behavior, not 200 with holds) |
| After `POST /api/holds/H-1042/pickup`, `GET /api/holds/overdue` | H-1042 absent (FR-8) |
| `ShelfApp(catalog)` with no `today` | Constructs, and `self.today` is `date.today` |
| Existing pickup tests | Unknown id 404, second pickup 409 (FR-11) |

**Done when.**
- All T3 tests, T1 and T2 tests, and the six existing tests pass.
- `GET /api/holds` and `POST /api/holds/{id}/pickup` responses are unchanged.
- `serve()` and `_handler_for` are unchanged apart from what the constructor needs (nothing). `log_message` still returns without writing.
- `index.html` is not touched.

---

## T4 — Long-waiting holds section on the page

**Outcome.** The page at `/` keeps the existing list and pickup button and adds a "Long-waiting holds" section below them that calls `GET /api/holds/overdue` with the librarian's window.

**Files.**
- `src/holdshelf/static/index.html`
- `tests/test_holdshelf.py`

**Depends on.** T3 (the endpoint and its response contract).

**Work.**
1. Leave the existing list, its message area, and the pickup button as they are. The existing list still shows no phone and no days waiting (AC-11).
2. Add a section headed "Long-waiting holds" below the existing list (Assumption 9) with:
   - A number input (`type="number"`, `min="1"`, `step="1"`, value `7`) (FR-3, Assumption 8).
   - A "Show long-waiting holds" button.
   - Its own message area and its own table: Hold, Title, Patron, Ready since, Days waiting, Phone.
3. On click:
   - Disable the button until the request finishes, then enable it (DR-15).
   - Always request `/api/holds/overdue?windowDays=` + `encodeURIComponent(input.value)`, including when the value is empty. Never omit the parameter and never substitute 7 (DR-1).
   - On 200 with a `holds` array: remember the response `windowDays`, render one row per hold with `textContent`, show `Not Found` when `phone` is `null` (FR-7, AC-6). An empty array shows "No ready hold is past the pickup window." (FR-9, AC-7).
   - On any other outcome: clear the long-waiting table. Show the server `error` text when the JSON body has one, "API unreachable" when `fetch` rejects, and "Could not load long-waiting holds." otherwise (DR-4). Do not touch the existing list or its message area.
4. After a successful pickup, if a long-waiting response has been remembered, reload the long-waiting view with the remembered `windowDays`, not the current input. Skip the reload when no long-waiting load has succeeded or when the pickup failed (DR-5, FR-8).
5. No phone or hold data in `console.log`.

**Tests (string checks on the page returned by `GET /`, matching the existing page test).**

| Check | Expected |
| --- | --- |
| Page contains `/api/holds/overdue` | yes |
| Page contains `windowDays=` and `encodeURIComponent` | yes (DR-1) |
| Page contains `Not Found` | yes (FR-7) |
| Page contains `No ready hold is past the pickup window.` | yes (FR-9) |
| Page contains `Could not load long-waiting holds.` and `API unreachable` | yes (DR-4) |
| Page contains `Long-waiting holds` and the number input with `min="1"` and `step="1"` | yes |
| Existing page test | Still passes (`Hold shelf`, `/api/holds`, `/api/health`) |

**Done when.**
- All page tests and every earlier test pass.
- The existing list and pickup button still work as before (verified by inspection here; exercised in a browser at Step 7).
- Server and catalog code are not touched by this task.

Browser checks are not part of T4. Step 7 (verifier) runs the page in a browser for a `Not Found` phone, the empty-list message, a 400 display, button disabling, and refresh after a successful pickup, using the actual run date (DR-6, DR-14). No implementation task starts the server for the user.

---

## Blocked list

| Task | Blocked until | Reason |
| --- | --- | --- |
| T3 | T1 and T2 are done | The route calls `Catalog.list_overdue` (T1) and `parse_window_days` / `BadWindowError` (T2) |
| T4 | T3 is done | The page depends on the endpoint path, the `{"windowDays", "holds"}` envelope, and the 400 `error` body that T3 delivers |

T1 and T2 are not blocked.

## First task free to start

**T1 — Overdue query in the catalog.** T2 is also free and can follow T1 (or go first if the user prefers), but the two should not run in parallel because both edit `tests/test_holdshelf.py`.

## Out of plan

- `CHANGELOG.md`, commits, and the pull request (Step 8, only when the user asks).
- Seed data changes (Assumption 12 keeps the seed as it is).
- Any change to `GET /api/holds`, pickup, `serve()`, or `log_message`.

## Not Found

- Named timezone. The server-local date is used (Decision 2).
