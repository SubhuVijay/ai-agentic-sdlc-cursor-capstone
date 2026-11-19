# Requirements — KAN-3

**Story:** KAN-3, Show holds that have waited past the pickup window
**Status in Jira:** To Do
**Source:** `docs/user-story.md`

## Context and goal

Lane Street Library already uses the hold shelf in `src/holdshelf`. A librarian can see every hold and mark a ready hold as picked up. The shelf does not show how long a book has been waiting, and it does not show the patron phone.

The librarian needs a long-waiting view on that same page: ready holds that have waited strictly longer than the pickup window, with the days waited and the patron phone, so they can call the patron and free the shelf. This story adds that view and `GET /api/holds/overdue`. It leaves the existing hold list and the pickup action in place.

## Decisions

1. The pickup window is 7 days by default. The librarian can change it on the page.
2. "Today" is the server's local date. A named timezone is Not Found.
3. A ready hold with no `readySince` is left out of the overdue list. No days value is shown for it, because it is not listed.
4. The API returns `phone` as JSON `null` when the patron has no number, the same as `GET /api/holds`. The long-waiting view shows `Not Found`.
5. `GET /api/holds` stays exactly as it is.
6. The window is the query parameter `windowDays` (for example `?windowDays=7`). When the parameter is omitted, the window is 7 days.
7. A non-numeric `windowDays` value is a bad window and returns 400. The response must not include a guessed hold list.
8. A hold that has waited exactly `windowDays` days is not past the window. Only a strictly longer wait is included.
9. A valid `windowDays` is a whole number from 1 to 3650. Zero, negative values (for example `-1`), decimal values (for example `7.5` or `7.0`), and values above 3650 return 400 with no hold list. The user confirmed the zero, negative, and decimal cases during design review (DR-13). The upper bound of 3650 was agreed later.
10. The 400 message does not repeat the rejected value. Its text is `windowDays must be a whole number of days from 1 to 3650.`

### Recorded confirmation

The user confirmed during design review (DR-13) that zero, negative, and decimal `windowDays` values return 400. This is a recorded decision, not an open item. The later agreed bound (decisions 9 and 10) completes the window rule.

## Functional requirements

- **FR-1.** The page at `/` still lists holds and can still mark one as picked up. It adds a way for the librarian to ask for the long-waiting holds.
- **FR-2.** When the librarian asks for that view, the page loads `GET /api/holds/overdue` and shows only holds that are still `ready` and have waited strictly longer than the pickup window.
- **FR-3.** The page offers a pickup window in days. It starts at 7. The librarian can change it. The overdue request uses the value chosen on the page.
- **FR-4.** `GET /api/holds/overdue` accepts `windowDays`. If `windowDays` is omitted, the server uses 7. A valid `windowDays` is a whole number from 1 to 3650.
- **FR-5.** Days waiting are whole calendar days from the hold's `readySince` date to the server-local today. The hold is included only when that count is greater than `windowDays`.
- **FR-6.** Each overdue hold includes the fields `GET /api/holds` already returns for a hold (`id`, `title`, `patron`, `readySince`, `status`, `phone`) and the number of days waiting. The JSON name of the days field is Not Found.
- **FR-7.** The long-waiting view shows the days waiting and the patron phone. When `phone` is JSON `null`, the page shows `Not Found`.
- **FR-8.** Picked-up holds are excluded. A ready hold with no `readySince` is excluded.
- **FR-9.** When no ready hold is past the window, the API returns a successful empty result and no error. The page tells the librarian that no ready hold is past the window.
- **FR-10.** A bad `windowDays` returns 400 with the error text in NFR-5. The response does not contain a hold list. Bad values are non-numeric, zero, negative, decimal, and above 3650 (decisions 7 and 9).
- **FR-11.** `GET /api/holds` is unchanged. `POST /api/holds/{id}/pickup` is unchanged: an unknown id returns 404, and a second pickup returns 409.

## Non-functional requirements

- **NFR-1.** The server decides "today" from its local date. Day counts do not use a client clock.
- **NFR-2.** An omitted `windowDays` uses 7. A present but unusable `windowDays` is rejected. The server does not substitute 7 and return a list.
- **NFR-3.** `phone` in the API stays JSON `null` when missing. The text `Not Found` is only the page display.
- **NFR-4.** The long-waiting view reads the hold shelf the application already has. It does not call an external circulation system.
- **NFR-5.** A bad `windowDays` returns the 400 error `windowDays must be a whole number of days from 1 to 3650.` The message does not repeat the rejected value (decision 10).

## Acceptance criteria

- **AC-1.** With the server-local date 18 November 2026 and `windowDays=7` (or with `windowDays` omitted), `GET /api/holds/overdue` includes H-1042, ready since 2 November (16 days), patron Maya Chen, phone `555-0142`. It does not include H-1048, ready since 16 November (2 days). It does not include H-0991, which is already picked up.
- **AC-2.** On that same date, H-1048 is included only when its 2 days waiting are strictly greater than `windowDays`. At `windowDays=7` it is excluded. At a window of exactly 2 days it is excluded.
- **AC-3.** A ready hold whose calendar-day wait equals `windowDays` is excluded. On 18 November 2026, a hold ready since 11 November has waited 7 days and is excluded for a 7-day window.
- **AC-4.** A ready hold with no `readySince` is absent from the overdue result for every window.
- **AC-5.** A picked-up hold is absent for every window.
- **AC-6.** On the long-waiting view, H-1042 shows 16 days and `555-0142` for the 18 November 2026 example. H-1048, when a shorter window includes it, shows `Not Found` for the phone. The API value for that phone is JSON `null`.
- **AC-7.** An overdue result with no holds is not an error. The page states that no ready hold is past the window.
- **AC-8.** `windowDays=abc`, `windowDays=7days`, and a present empty `windowDays` return 400 and no hold list. Omitting `windowDays` does not return 400.
- **AC-9.** `windowDays=0`, `windowDays=-1`, `windowDays=7.5`, and `windowDays=7.0` return 400 and no hold list. The user confirmed this during design review (DR-13).
- **AC-10.** `GET /api/holds` still returns every hold with `id`, `title`, `patron`, `readySince`, `status` (`ready` or `picked-up`), and `phone`. The page can still mark a ready hold picked up. An unknown pickup id returns 404. A second pickup returns 409.
- **AC-11.** The existing list does not show the phone and does not show days waiting. Those appear on the long-waiting view.
- **AC-12.** `windowDays=3650` is accepted. `windowDays=3651` returns 400 with no hold list. The 400 body contains the NFR-5 text and does not repeat `3651`.

## Error and edge cases

- **Bad window.** Non-numeric, zero, negative, decimal, and above-3650 `windowDays` values return 400 with the NFR-5 error and no hold list. A missing parameter is not a bad window; it means 7 days.
- **Missing hold.** The overdue endpoint returns only holds that are on the shelf and match the rules above. It does not invent a hold. Pickup of an unknown id still returns 404 and does not change the shelf. There is no overdue lookup by hold id in this story.
- **Missing `readySince`.** A ready hold with no `readySince` is left out. The days field is not shown for that hold.
- **Empty overdue list.** A successful request whose filters match nothing returns an empty result. The page tells the librarian that no ready hold is past the window.
- **Not Found phones.** JSON `null` in `GET /api/holds` and in `GET /api/holds/overdue`. The long-waiting page shows `Not Found`. The existing hold list still does not show the phone.
- **Exact window length.** Wait days equal to `windowDays` stay off the overdue list.
- **Picked up.** Status `picked-up` stays off the overdue list even when the wait is longer than the window. H-0991 in the 18 November 2026 example is this case.

## Out of scope

- Sending email or SMS
- Connecting to the city library circulation system
- Changing how a hold is marked picked up
- Fines, renewals, and checkout
- Replacing `GET /api/holds` or the existing list on `/`

## Not Found

- Named timezone. The decision is server local time only.
- Stored string format of `readySince`. The story gives calendar dates, not a format.
- JSON property name for the days-waiting count.
- JSON envelope of `GET /api/holds/overdue` (a bare array or an object).
- Sort order of the overdue holds.
- Page control type used to edit the window (text field, stepper, or other).
- Whether the long-waiting view is shown together with the full list or in its place, beyond this rule: the full list and pickup action remain available, and the long-waiting view itself shows only the overdue holds.
- Titles and other patron details not stated in the story example. H-1042's title is Not Found. H-1048's patron name is Not Found.
