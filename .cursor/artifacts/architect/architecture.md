# Architecture — KAN-3

**Story:** KAN-3, Show holds that have waited past the pickup window
**Input:** `.cursor/artifacts/requirements-agent/requirements.md` (approved)
**Extends:** the existing app in `src/holdshelf` (`catalog.py`, `server.py`, `static/index.html`)

## Approved decisions carried in

- Omitted `windowDays` means 7. Non-numeric, empty, zero, negative, and decimal values (including `7.0`) return 400 with a clear error and no hold list. The user confirmed the zero, negative, and decimal cases, so AC-9 is a firm requirement now.
- A hold that has waited exactly `windowDays` days is not overdue. Only a strictly longer wait counts.
- "Today" is the server-local date.
- `phone` is JSON `null` in the API. The page shows `Not Found`.
- A ready hold with no `readySince` is left off the overdue list.
- `GET /api/holds` and `POST /api/holds/{id}/pickup` do not change.
- The librarian can change the window on the page.

## Design review decisions

The user agreed to these on the design-review pass. They revise Assumption 5, Assumption 8, Assumption 10, and Assumption 11 where those assumptions said something different. The other assumptions stay as accepted.

- **DR-1.** The page always sends `windowDays`, including when the input is blank (`windowDays=`). A blank or non-numeric input returns 400. The page does not omit the parameter and does not substitute 7.
- **DR-2.** A valid window is a whole number from 1 to 3650. A value above 3650 returns 400. This replaces Assumption 5's "no upper bound". Leading zeros such as `07` are accepted as 7 when the numeric value is in range. `00` is 0 and returns 400. A digit string that `int()` cannot convert is a bad window and returns 400, not an uncaught exception.
- **DR-3.** The digit check is `re.fullmatch(r"[0-9]+", value)`, then the integer must be from 1 to 3650. Tests cover `+7`, a leading space (`%207`), a trailing newline (`7%0A`), `00`, and `07`.
- **DR-4.** If the long-waiting request is not 200 with a `holds` list (network failure, non-JSON, 404, or 500), the page clears that table and shows the server `error` text, or "Could not load long-waiting holds.", or "API unreachable" when the server cannot be reached. The existing list stays untouched.
- **DR-5.** After a successful pickup, the page refreshes the long-waiting view with the `windowDays` from the last successful long-waiting response, not the current input. It skips that refresh when the view has never loaded successfully, and when the pickup failed.
- **DR-6.** Unit tests use the injected date 18 November 2026 and the matrix in "Tests" below. Step 7 checks the page in a browser for a `Not Found` phone, the empty message, a 400 display, and refresh after pickup, using the actual run date.
- **DR-7.** `parse_window_days` and `BadWindowError` live in `server.py`. `Catalog.list_overdue` owns the filter, the `daysWaiting` count, and the sort. The route only parses, calls, and wraps the result.
- **DR-8.** `date.fromisoformat` may accept more than `YYYY-MM-DD` on Python 3.11 and later. That difference is accepted. The seed and the tests use `YYYY-MM-DD`. `list_overdue` catches `ValueError` and `TypeError` and skips the hold. There is no strict pre-parse regex.
- **DR-9.** This story adds no catch-all for unexpected exceptions in `handle`.
- **DR-10.** The 400 message does not include the rejected value. The body is `{"error": "windowDays must be a whole number of days from 1 to 3650."}` with no `holds` key.
- **DR-11.** `GET /api/holds` ignores `windowDays` and keeps its current output.
- **DR-12.** A misspelled parameter name, such as `windowdays` or `window`, is treated as omitted and uses 7. Unknown parameters are ignored. The response includes the applied `windowDays`.
- **DR-13.** The user confirmed that zero, negative, and decimal `windowDays` values return 400 with no hold list. That confirmation is recorded here. `requirements.md` still has the older "Confirm" wording; the requirements agent owns that file.
- **DR-14.** AC-1 to AC-6 are proven by unit tests with the injected date 18 November 2026. The Step 7 browser check compares the page with the counts for the actual run date, and the verification report states that date.
- **DR-15.** The long-waiting button is disabled while its request is in flight, the same way the pickup button is disabled during a pickup.
- **DR-16.** `ShelfApp.__init__(self, catalog=None, *, today=None)`. `today` is an optional keyword-only argument after `catalog` and defaults to `date.today`. Only the type of `Hold.ready_since` changes, to `str | None`. The field stays where it is and has no default.

## Existing app (as found)

- `catalog.py` has the `Hold` dataclass (`id`, `title`, `patron`, `ready_since`, `status`, `phone`), the seed shelf, and `Catalog` with `list_holds()`, `mark_picked_up()`, and `to_dict()`. The seed stores `ready_since` as an ISO `YYYY-MM-DD` string.
- `server.py` has `ShelfApp.handle(method, target)`, which routes on the URL path and returns `(status, payload)`. It uses only the URL path today and ignores the query string. `_handler_for` wraps it in a standard-library `BaseHTTPRequestHandler`, and `log_message` is overridden to log nothing.
- `static/index.html` is one page with inline JavaScript. It calls `/api/health`, then `/api/holds`, renders a table, and posts pickups.
- `tests/test_holdshelf.py` tests `ShelfApp.handle` directly with an injected `Catalog`, without opening a socket.

## Component diagram

```mermaid
flowchart LR
    Librarian([Librarian])

    subgraph Browser
        Page["index.html<br/>Hold list (unchanged)<br/>+ Long-waiting view"]
    end

    subgraph "holdshelf server (Python stdlib)"
        Handler["HTTP Handler<br/>_handler_for<br/>(log_message silent)"]
        App["ShelfApp.handle<br/>routing"]
        Window["Window parser<br/>parse_window_days"]
        Overdue["Overdue query<br/>Catalog.list_overdue"]
        Clock["Today provider<br/>server-local date"]
        Catalog["Catalog<br/>in-memory holds"]
    end

    Librarian -->|sets window, asks for view| Page
    Page -->|GET /api/holds/overdue?windowDays=N| Handler
    Page -->|GET /api/holds, POST pickup (unchanged)| Handler
    Handler --> App
    App -->|raw windowDays| Window
    Window -->|valid int or error| App
    App -->|window, today| Overdue
    Clock -->|today| App
    Overdue --> Catalog
    App -->|200 JSON or 400 JSON| Handler
    Handler --> Page
```

## Components and responsibilities

| Component | File | Change |
| --- | --- | --- |
| Hold model and catalog | `catalog.py` | Extended |
| Overdue query | `catalog.py` | New method |
| Window parser | `server.py` | New |
| Today provider | `server.py` | New, injectable |
| Routing | `server.py` `ShelfApp.handle` | Extended with one route |
| HTTP handler | `server.py` `_handler_for` | Unchanged |
| Page | `static/index.html` | Extended with a long-waiting view |

- **Hold model and catalog.** Still the single source of holds (NFR-4). Only the type of `Hold.ready_since` changes, from `str` to `str | None`, so a ready hold with no `readySince` can exist (DR-16). The field stays the fourth field, after `patron` and before `status`, and it has no default. `to_dict()` and `list_holds()` keep their current keys and order. `GET /api/holds` ignores any query string, including `windowDays`, so its output stays the same (FR-11, DR-11).
- **Overdue query: `Catalog.list_overdue(window_days: int, today: date) -> list[dict]`.** This method owns the filter, the `daysWaiting` count, and the sort (DR-7). For each hold it keeps only `status == "ready"`, skips a missing `ready_since`, and parses with `date.fromisoformat`. `ValueError` and `TypeError` skip that hold. There is no strict format regex before the parse (DR-8). `days_waiting = (today - ready).days`, and the hold is kept only when `days_waiting > window_days` (FR-5, FR-8, AC-3). A future `readySince` gives a negative count and is left out. Each result is `to_dict(hold)` plus `daysWaiting`, so the existing fields and the `null` phone come along unchanged (FR-6, NFR-3). Results are ordered by `daysWaiting` descending, then `id` ascending (Assumption 3). The query does not validate the window. It receives an int that has already been checked.
- **Window parser: `parse_window_days(raw: list[str] | None) -> int` and `BadWindowError`, both in `server.py`.** One function holds all the window rules. Omitted (`None` or an empty list) means 7. One value must satisfy `re.fullmatch(r"[0-9]+", value)` and then be an integer from 1 to 3650 (DR-2, DR-3). `07` is 7 and is accepted. `00` is 0 and is rejected. Above 3650 is rejected. If `int()` raises `ValueError` on a very long digit string, that is also a bad window. This rejects `abc`, `7days`, an empty value, `0`, `-1`, `7.5`, `7.0`, `+7`, a leading space, a trailing newline, and a repeated parameter (FR-10, AC-8, AC-9). The regex is `fullmatch` with `[0-9]`, not `^...$` and not `\d`, because `int()` accepts `" 7"`, `"+7"`, and non-ASCII digits, and `^...$` accepts a trailing newline. `BadWindowError` carries the fixed message `windowDays must be a whole number of days from 1 to 3650.` and does not include the rejected value (DR-10).
- **Today provider.** `ShelfApp.__init__(self, catalog: Catalog | None = None, *, today: Callable[[], date] | None = None)`. `today` is keyword-only, after `catalog`, and defaults to `date.today` (DR-16, NFR-1). `ShelfApp(catalog)` still works. Tests pass `today=` with 18 November 2026.
- **Routing.** `ShelfApp.handle` adds `GET /api/holds/overdue` only. `GET /api/holds` does not read the query string (DR-11). The overdue route parses the query with `urllib.parse.parse_qs(urlparse(target).query, keep_blank_values=True)` so that `windowDays=` reaches the parser as a present empty value. Only the parameter name `windowDays` counts. A misspelled name is treated as omitted and uses 7, and other parameters are ignored (DR-12). The new route is matched as an exact path before the fallback 404. It does not collide with the pickup route, which needs the `/pickup` suffix. There is no catch-all around `handle` (DR-9). On success the route returns `200, {"windowDays": n, "holds": list_overdue(...)}`. On `BadWindowError` it returns `400, {"error": "windowDays must be a whole number of days from 1 to 3650."}` with no `holds` key (FR-10, NFR-2, DR-10).
- **HTTP handler.** No change. It serializes the payload and already writes no access log.
- **Page.** The existing list and pickup button stay as they are and still do not show phone or days waiting (AC-11). A new "Long-waiting holds" section below the list has a whole-number input that starts at 7, a "Show long-waiting holds" button, its own message area, and its own table: Hold, Title, Patron, Ready since, Days waiting, Phone. Values are written with `textContent`, as the page does today. A `null` phone is shown as `Not Found` (FR-7). An empty `holds` array shows "No ready hold is past the pickup window." (FR-9, AC-7). The page always requests `GET /api/holds/overdue?windowDays=` plus `encodeURIComponent` of the input value, including when that value is empty (DR-1). It does not omit the parameter and does not substitute 7. The button is disabled while that request is in flight and enabled again when it finishes (DR-15). On any result other than 200 with a `holds` array, the page clears the long-waiting table. It shows the server `error` text when the body has one, "API unreachable" when `fetch` fails, and "Could not load long-waiting holds." otherwise (DR-4). The existing list and its message area are not changed by these outcomes. After a 200, the page remembers the response `windowDays`. A successful pickup reloads the long-waiting view with that remembered value. A failed pickup, or a pickup before any successful long-waiting load, does not call the overdue endpoint (DR-5).

## Technology choice

- **Python standard library only** (`http.server`, `urllib.parse`, `datetime`, `re`, `json`). The app already says the standard library is its only dependency. The feature needs only date arithmetic, query parsing, and JSON, so a framework or a date library adds nothing.
- **`datetime.date` and `date.fromisoformat`** give whole calendar-day differences without time-of-day or DST effects. That matches "whole calendar days to the server-local today" (FR-5). On Python 3.11 and later, `fromisoformat` also accepts some non-`YYYY-MM-DD` forms. That difference is accepted (DR-8). The seed and the tests use `YYYY-MM-DD`, and a value that raises `ValueError` or `TypeError` is left off the list.
- **In-memory `Catalog`.** The story reads the shelf the app already has and calls no external system (NFR-4). No database is added.
- **Plain HTML and inline JavaScript using `fetch`.** This matches the current page. No build step and no front-end framework are added.
- **`unittest` against `ShelfApp.handle`.** This matches `tests/test_holdshelf.py`. Injecting the catalog and the today provider makes the date-based acceptance criteria repeatable.

## Data flow

1. The librarian opens `/`. The page calls `GET /api/health`, then `GET /api/holds`, and renders the existing list. This part does not change.
2. The librarian leaves the window at 7 or types another value, then clicks "Show long-waiting holds". The button stays disabled until the request finishes.
3. The page always sends `GET /api/holds/overdue?windowDays=<typed value>`, including `windowDays=` when the input is blank.
4. `Handler._respond` passes the method and target to `ShelfApp.handle`.
5. `handle` matches `/api/holds/overdue` and reads only the `windowDays` values from the query string. A missing or misspelled name is omitted.
6. `parse_window_days` returns 7 when the parameter is omitted, returns the int when it is a whole number from 1 to 3650, and raises `BadWindowError` otherwise.
   - Bad value: `handle` returns `400, {"error": "windowDays must be a whole number of days from 1 to 3650."}`. The message does not include the rejected value. The page shows that text and clears the long-waiting table.
   - Any other failure (network, non-JSON, or a status other than 200 with a `holds` list) also clears that table and shows "API unreachable" or "Could not load long-waiting holds." The existing list stays as it is.
7. Valid value: `handle` calls `today()`, then `catalog.list_overdue(window, today)`.
8. `list_overdue` keeps ready holds that have a parseable `ready_since` and wait days strictly greater than the window, adds `daysWaiting`, and sorts longest wait first.
9. `handle` returns `200, {"windowDays": window, "holds": [...]}`, and the handler writes it as JSON. The page stores that `windowDays`.
10. The page renders one row per hold, with the days waiting and either the phone or `Not Found`. When the array is empty, it shows the no-overdue message.
11. After a successful pickup, if a long-waiting response has already been stored, the page reloads that view with the stored `windowDays`, so a picked-up hold leaves it (FR-8, DR-5). A failed pickup does not reload it.

## Secrets and patron phone numbers

- **No access log.** `Handler.log_message` already returns without writing. The design keeps it that way, so request lines (which hold the query string) and client addresses are not written to stderr.
- **No logging of payloads or holds.** The new code adds no `print` or `logging` calls with hold data. The only startup output is the existing host and port line in `serve()`.
- **Phone appears only in the response body.** The phone goes from `Catalog` into the JSON response and is displayed in the page. It is not in error messages, in the 400 body, or in exception text. The 400 message is the fixed sentence in DR-10 and does not repeat the rejected `windowDays` value (DR-10). The page shows it with `textContent`.
- **No secrets in the app.** The hold shelf server reads no tokens, `.env`, or `config/jira.local.json`. Those files are used only by `scripts/load_user_story.py` for loading the story, and nothing in `src/holdshelf` imports them. The design adds no configuration that holds a secret.
- **Local bind.** The server stays on `127.0.0.1:8765`, so the phone list is not exposed beyond the machine running it.

## Not Found

- Named timezone (the decision is server local time only)
- Titles and patron details not given in the story example. The repository seed data has values for them, but the story does not.

The 400 wording and the upper bound were Not Found in the requirements. Design review settled both: the message in DR-10, and the range 1 to 3650 in DR-2.

## Assumptions

These fill gaps that the requirements mark as Not Found. The user accepted all twelve, and design review revised 5, 8, 10, and 11 as noted.

1. **Days field name:** `daysWaiting` (an integer), in camelCase to match `readySince`.
2. **Response envelope:** `{"windowDays": <int>, "holds": [ ... ]}`. This matches the `{"holds": [...]}` shape of `GET /api/holds` and echoes the window that was applied, which helps confirm that an omitted parameter meant 7.
3. **Sort order:** `daysWaiting` from most to fewest, then `id` ascending to break ties, so the longest waits come first.
4. **`readySince` format:** ISO `YYYY-MM-DD`, which is how the existing seed stores it. A ready hold whose `readySince` is `None`, empty, or cannot be parsed as an ISO date is treated as missing and left off the overdue list. Nothing is guessed for it.
5. **Window range 1 to 3650.** Revised by DR-2. The earlier "no upper bound" is withdrawn. A whole number from 1 to 3650 is valid. Above 3650 returns 400. Leading zeros such as `07` are accepted as 7 when the numeric value is in range. `00` is 0 and returns 400.
6. **Repeated parameter:** `?windowDays=7&windowDays=9` is ambiguous, so it returns 400.
7. **Surrounding whitespace, a `+` sign, and non-ASCII digits** are bad values and return 400.
8. **Page control:** a number input (`type="number"`, `min="1"`, `step="1"`) that starts at 7, plus a button. The browser hint does not replace the server check. The page always sends the input value, including a blank one (DR-1). The button is disabled while the request is in flight (DR-15). If the server rejects the value, the page shows the server's 400 message and clears the long-waiting table.
9. **Layout:** the long-waiting view is a separate section below the existing list on the same page. The full list and the pickup action are always visible.
10. **Refresh after pickup:** after a successful pickup, the page reloads the long-waiting view with the `windowDays` from the last successful overdue response, not the current input (DR-5). It does not reload that view when none has loaded, or when the pickup failed.
11. **Model change:** `Hold.ready_since` becomes `str | None` and stays the fourth field with no default (DR-16). `to_dict` sends `None` as JSON `null` in `GET /api/holds`. Today's seed has no such hold, so the current output of `GET /api/holds` does not change. `ShelfApp` gains a keyword-only `today` argument after `catalog`.
12. **Seed data stays as it is.** The current seed already covers AC-1 (H-1042 at 16 days, H-1048 at 2 days with no phone, H-0991 picked up). Edge cases such as exactly 7 days and a missing `readySince` are covered with injected catalogs in tests instead of new seed rows.

## Tests

Unit tests call `ShelfApp.handle` with an injected catalog and `today` fixed at 18 November 2026 (DR-6, DR-14). They do not open a socket. The page source is still checked as a string. The live page is checked in the browser at Step 7 against the actual run date, and the verification report states that date.

| Case | Expected |
| --- | --- |
| Omitted `windowDays` | 200, `windowDays` 7, H-1042 with `daysWaiting` 16 and phone `555-0142` |
| `windowDays=7` and `windowDays=07` | Same as omitted for the list. `07` is applied as 7 |
| Ready since 11 November 2026, window 7 | Excluded (waited exactly 7 days) |
| H-1048 at window 1 | Included, `daysWaiting` 2, `phone` JSON `null` |
| H-1048 at window 2 | Excluded |
| Picked-up hold older than the window | Excluded for every window |
| Ready hold with `ready_since` `None`, empty, or unparseable | Excluded for every window, no error |
| Ready hold with a future `readySince` | Excluded, no error |
| No hold matches | 200, `holds` is `[]` |
| Sort | `daysWaiting` descending, then `id` ascending |
| `abc`, `7days`, empty, `?windowDays` with no `=`, `0`, `00`, `-1`, `7.5`, `7.0`, `+7`, `%207`, `7%0A`, a repeated `windowDays`, `3651`, and a digit string `int()` cannot convert | 400, `error` is `windowDays must be a whole number of days from 1 to 3650.`, no `holds` key |
| `windowDays=3650` with the seed catalog | 200, not a 400. Every seed hold has waited fewer than 3650 days, so `holds` is `[]` |
| Misspelled `windowdays=abc` | 200, applied `windowDays` 7 |
| `GET /api/holds?windowDays=abc` | 200, the full list, unchanged keys and order |
| Existing pickup tests | Still pass: unknown id 404, second pickup 409 |

The page test checks that `/` contains `/api/holds/overdue`, `Not Found`, and "No ready hold is past the pickup window." Step 7 exercises the page in a browser for a `null` phone shown as `Not Found`, the empty-list message, a 400 display, and refresh after a successful pickup.
