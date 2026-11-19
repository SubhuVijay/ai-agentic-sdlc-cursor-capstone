# KAN-3: Show holds that have waited past the pickup window

**Jira:** KAN-3 (Story)
**Status:** To Do

## User story

As a librarian at Lane Street Library, I want the hold shelf to show which ready holds have been waiting past the pickup window, so that I can call those patrons and free the shelf.


## What already exists

The hold shelf application in src/holdshelf is already in use at the desk.

- GET /api/health returns { "status": "ok" }.
- GET /api/holds returns every hold: id, title, patron, readySince, status (ready or picked-up), and phone. Phone is JSON null when the patron record has no number.
- POST /api/holds/{id}/pickup marks a ready hold as picked up. An unknown id returns 404. A second pickup returns 409.
- The page at / lists the holds and can mark one as picked up. It does not show the phone, and it does not say how long a book has been waiting.

This story adds to that application. It does not replace the list or the pickup action.


## Requested change

- Add a way on the existing page to show only the holds that are still ready and have waited longer than the pickup window.
- Show the number of days each of those holds has been waiting, counted from readySince to today.
- Show the patron phone on that view. When the phone is missing, show Not Found.
- Add GET /api/holds/overdue for that same set of holds. The page loads it when the librarian asks for the long-waiting holds.
- Keep picked-up holds out of that result.
- An empty result tells the librarian that no ready hold is past the window.
- Reject a bad window value with 400 and a clear error. Do not guess a list.


## Example

On 18 November 2026, with a 7-day window, GET /api/holds/overdue includes H-1042 (ready since 2 November, Maya Chen, 555-0142) and does not include H-1048 (ready since 16 November) or H-0991 (already picked up). H-1048 would appear only in a shorter window, and its phone is Not Found.


## Out of scope

- Sending email or SMS
- Connecting to the city library circulation system
- Changing how a hold is marked picked up
- Fines, renewals, and checkout


## Open questions

1. Is the pickup window 7 days, and can the librarian change it on the page?
2. Which timezone decides "today" when counting days?
3. Should a ready hold with no readySince be listed, and what should the days field show?
4. Is Not Found the phone value in the API response as well as on the page?
5. Should GET /api/holds stay exactly as it is?
