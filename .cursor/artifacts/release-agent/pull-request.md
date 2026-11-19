## Summary

Lane Street Library staff can already list holds and mark a ready hold picked up. This change adds the long-waiting view from KAN-3 so a librarian can see which ready holds have waited past the pickup window, how many days they have waited, and the patron phone to call. The existing list and pickup action stay on the same page. `GET /api/holds/overdue` serves that view, using the server-local date and a pickup window the librarian can change.

## Changes Made

- `src/holdshelf/catalog.py` — `Hold.ready_since` may be missing. `Catalog.list_overdue` keeps ready holds whose wait is strictly longer than the window, adds `daysWaiting`, and sorts the longest wait first.
- `src/holdshelf/server.py` — `parse_window_days` accepts a whole number from 1 to 3650 (default 7) and rejects anything else with a fixed 400 message. `GET /api/holds/overdue` returns `{ "windowDays", "holds" }`. "Today" defaults to the server-local date and can be injected in tests.
- `src/holdshelf/static/index.html` — Adds the long-waiting section: a window input starting at 7, **Show long-waiting holds**, days waiting, and the phone or `Not Found`. The existing list and **Mark picked up** stay. A successful pickup refreshes the long-waiting view. The button is disabled while the overdue request is in flight.
- `tests/test_holdshelf.py` — Covers the overdue query, the window parser, the overdue route, the unchanged list and pickup routes, and the page markup for the long-waiting section.
- `docs/user-story.md` — Holds the loaded KAN-3 story, "Show holds that have waited past the pickup window."
- `CHANGELOG.md` — Records the KAN-3 hold-shelf behavior under `## [Unreleased]`.
- `.cursor/artifacts/requirements-agent/requirements.md` — Approved requirements for KAN-3.
- `.cursor/artifacts/architect/architecture.md` — Approved architecture, including the design-review decisions.
- `.cursor/artifacts/design-reviewer/design-review.md` — Design review of that architecture.
- `.cursor/artifacts/planner/impl-plan.md` — Implementation plan for tasks T1 to T4.
- `.cursor/artifacts/code-reviewer/code-review.md` — Code review of T1 to T4. DRY-1 stays deferred.
- `.cursor/artifacts/verifier/verification-report.md` — Passing test run and browser check for 20 November 2026.
- `.cursor/artifacts/release-agent/pull-request.md` — This pull request description.

## Test Evidence

From `.cursor/artifacts/verifier/verification-report.md`. Run date: 20 November 2026. No product code was changed during verification.

Command:

```text
python -m unittest discover -s tests -v
```

Exit code: 0. Ran 65 tests in 0.190s. Result: OK.

```text
test_cli_denies_dotenv (test_guard_secrets.GuardSecretsTests.test_cli_denies_dotenv) ... ok
test_project_files_are_allowed (test_guard_secrets.GuardSecretsTests.test_project_files_are_allowed) ... ok
test_secret_files_are_denied (test_guard_secrets.GuardSecretsTests.test_secret_files_are_denied) ... ok
test_cli_allows_git_status (test_guard_shell.GuardShellTests.test_cli_allows_git_status) ... ok
test_destructive_git_asks_for_confirmation (test_guard_shell.GuardShellTests.test_destructive_git_asks_for_confirmation) ... ok
test_env_example_read_is_allowed (test_guard_shell.GuardShellTests.test_env_example_read_is_allowed) ... ok
test_ordinary_git_commands_are_allowed (test_guard_shell.GuardShellTests.test_ordinary_git_commands_are_allowed) ... ok
test_secret_reads_are_denied (test_guard_shell.GuardShellTests.test_secret_reads_are_denied) ... ok
test_health (test_holdshelf.HoldShelfTests.test_health) ... ok
test_lists_holds_and_keeps_a_missing_phone_as_null (test_holdshelf.HoldShelfTests.test_lists_holds_and_keeps_a_missing_phone_as_null) ... ok
test_page_includes_the_long_waiting_section (test_holdshelf.HoldShelfTests.test_page_includes_the_long_waiting_section) ... ok
test_page_loads_the_hold_api (test_holdshelf.HoldShelfTests.test_page_loads_the_hold_api) ... ok
test_pickup_marks_the_hold_and_rejects_a_second_pickup (test_holdshelf.HoldShelfTests.test_pickup_marks_the_hold_and_rejects_a_second_pickup) ... ok
test_unknown_hold_returns_404 (test_holdshelf.HoldShelfTests.test_unknown_hold_returns_404) ... ok
test_unknown_path_returns_404 (test_holdshelf.HoldShelfTests.test_unknown_path_returns_404) ... ok
test_exact_seven_days_is_excluded (test_holdshelf.OverdueQueryTests.test_exact_seven_days_is_excluded) ... ok
test_future_ready_since_is_excluded (test_holdshelf.OverdueQueryTests.test_future_ready_since_is_excluded) ... ok
test_h1048_is_excluded_at_window_2 (test_holdshelf.OverdueQueryTests.test_h1048_is_excluded_at_window_2) ... ok
test_h1048_is_included_at_window_1_with_a_null_phone (test_holdshelf.OverdueQueryTests.test_h1048_is_included_at_window_1_with_a_null_phone) ... ok
test_hold_accepts_a_missing_ready_since (test_holdshelf.OverdueQueryTests.test_hold_accepts_a_missing_ready_since) ... ok
test_list_holds_keeps_a_missing_ready_since (test_holdshelf.OverdueQueryTests.test_list_holds_keeps_a_missing_ready_since) ... ok
test_missing_or_unparseable_ready_since_is_excluded (test_holdshelf.OverdueQueryTests.test_missing_or_unparseable_ready_since_is_excluded) ... ok
test_picked_up_hold_is_excluded (test_holdshelf.OverdueQueryTests.test_picked_up_hold_is_excluded) ... ok
test_result_keys (test_holdshelf.OverdueQueryTests.test_result_keys) ... ok
test_seed_window_3650_returns_an_empty_list (test_holdshelf.OverdueQueryTests.test_seed_window_3650_returns_an_empty_list) ... ok
test_seed_window_7_returns_only_the_sixteen_day_hold (test_holdshelf.OverdueQueryTests.test_seed_window_7_returns_only_the_sixteen_day_hold) ... ok
test_sorts_longest_wait_first_then_id (test_holdshelf.OverdueQueryTests.test_sorts_longest_wait_first_then_id) ... ok
test_bad_windows_return_the_fixed_error (test_holdshelf.OverdueRouteTests.test_bad_windows_return_the_fixed_error) ... ok
test_exact_seven_day_wait_is_excluded (test_holdshelf.OverdueRouteTests.test_exact_seven_day_wait_is_excluded) ... ok
test_hold_list_ignores_the_window_query (test_holdshelf.OverdueRouteTests.test_hold_list_ignores_the_window_query) ... ok
test_missing_ready_since_is_excluded (test_holdshelf.OverdueRouteTests.test_missing_ready_since_is_excluded) ... ok
test_misspelled_window_names_use_the_default (test_holdshelf.OverdueRouteTests.test_misspelled_window_names_use_the_default) ... ok
test_omitted_window_returns_the_sixteen_day_hold (test_holdshelf.OverdueRouteTests.test_omitted_window_returns_the_sixteen_day_hold) ... ok
test_other_parameters_are_ignored (test_holdshelf.OverdueRouteTests.test_other_parameters_are_ignored) ... ok
test_picked_up_hold_is_excluded (test_holdshelf.OverdueRouteTests.test_picked_up_hold_is_excluded) ... ok
test_pickup_removes_the_hold_from_the_overdue_view (test_holdshelf.OverdueRouteTests.test_pickup_removes_the_hold_from_the_overdue_view) ... ok
test_pickup_still_reports_unknown_and_repeat_pickup (test_holdshelf.OverdueRouteTests.test_pickup_still_reports_unknown_and_repeat_pickup) ... ok
test_post_overdue_is_not_the_overdue_view (test_holdshelf.OverdueRouteTests.test_post_overdue_is_not_the_overdue_view) ... ok
test_today_defaults_to_the_server_date (test_holdshelf.OverdueRouteTests.test_today_defaults_to_the_server_date) ... ok
test_window_1_includes_the_hold_with_no_phone (test_holdshelf.OverdueRouteTests.test_window_1_includes_the_hold_with_no_phone) ... ok
test_window_2_excludes_h1048 (test_holdshelf.OverdueRouteTests.test_window_2_excludes_h1048) ... ok
test_window_3650_returns_an_empty_list (test_holdshelf.OverdueRouteTests.test_window_3650_returns_an_empty_list) ... ok
test_window_7_and_07_match_the_omitted_window (test_holdshelf.OverdueRouteTests.test_window_7_and_07_match_the_omitted_window) ... ok
test_above_the_upper_bound_is_rejected (test_holdshelf.WindowParserTests.test_above_the_upper_bound_is_rejected) ... ok
test_lower_and_upper_bounds (test_holdshelf.WindowParserTests.test_lower_and_upper_bounds) ... ok
test_non_numeric_values_are_rejected (test_holdshelf.WindowParserTests.test_non_numeric_values_are_rejected) ... ok
test_omitted_window_defaults_to_seven (test_holdshelf.WindowParserTests.test_omitted_window_defaults_to_seven) ... ok
test_repeated_window_is_rejected (test_holdshelf.WindowParserTests.test_repeated_window_is_rejected) ... ok
test_seven_with_and_without_a_leading_zero (test_holdshelf.WindowParserTests.test_seven_with_and_without_a_leading_zero) ... ok
test_signs_spaces_newlines_and_non_ascii_digits_are_rejected (test_holdshelf.WindowParserTests.test_signs_spaces_newlines_and_non_ascii_digits_are_rejected) ... ok
test_very_long_digit_string_is_rejected (test_holdshelf.WindowParserTests.test_very_long_digit_string_is_rejected) ... ok
test_zero_negative_and_decimal_values_are_rejected (test_holdshelf.WindowParserTests.test_zero_negative_and_decimal_values_are_rejected) ... ok
test_blank_jira_token_is_rejected (test_jira_config.StorySourceTests.test_blank_jira_token_is_rejected) ... ok
test_confluence_storage_becomes_text (test_jira_config.StorySourceTests.test_confluence_storage_becomes_text) ... ok
test_example_config_has_no_token (test_jira_config.StorySourceTests.test_example_config_has_no_token) ... ok
test_file_source_does_not_need_a_token (test_jira_config.StorySourceTests.test_file_source_does_not_need_a_token) ... ok
test_flat_jira_config_strips_the_base_url (test_jira_config.StorySourceTests.test_flat_jira_config_strips_the_base_url) ... ok
test_missing_config_leaves_the_story_in_place (test_jira_config.StorySourceTests.test_missing_config_leaves_the_story_in_place) ... ok
test_missing_file_names_the_example (test_jira_config.StorySourceTests.test_missing_file_names_the_example) ... ok
test_word_document_becomes_markdown (test_jira_config.StorySourceTests.test_word_document_becomes_markdown) ... ok
test_cli_emits_additional_context (test_sdlc_context.GateReportTests.test_cli_emits_additional_context) ... ok
test_completed_planning_gates (test_sdlc_context.GateReportTests.test_completed_planning_gates) ... ok
test_missing_gates_point_at_requirements (test_sdlc_context.GateReportTests.test_missing_gates_point_at_requirements) ... ok
test_next_gate_is_the_first_missing_artifact (test_sdlc_context.GateReportTests.test_next_gate_is_the_first_missing_artifact) ... ok
test_root_level_artifact_does_not_pass_the_gate (test_sdlc_context.GateReportTests.test_root_level_artifact_does_not_pass_the_gate) ... ok
No config/jira.local.json. Using docs/user-story.md
Wrote C:\Users\SUBRAM~1\AppData\Local\Temp\tmpimmn22b9\user-story.md from C:\Users\SUBRAM~1\AppData\Local\Temp\tmpimmn22b9\story.docx

----------------------------------------------------------------------
Ran 65 tests in 0.190s

OK
```

Browser check on the running page at http://127.0.0.1:8765/ (headless Chrome; the Playwright browser tool was unavailable). Server-local date: 20 November 2026. Passed for:

- Window 1 shows H-1048's phone as `Not Found`. The API value is JSON `null`. The page text does not use `Not Found` as an API value.
- Window 3650 shows `No ready hold is past the pickup window.`
- Bad windows (`abc` via the HTTP API, and empty, `0`, `-1`, `7.5`, and `3651` on the page) show `windowDays must be a whole number of days from 1 to 3650.` and clear the long-waiting table. The number input cannot hold `abc`, so that case was confirmed on the HTTP request.
- **Show long-waiting holds** was disabled while each overdue request was in flight (17 samples, all disabled) and enabled again when the request finished.
- After a successful window of 1, changing the input to 3650 without clicking the button, then **Mark picked up** on H-1042, refreshed the long-waiting view from `windowDays=1`. H-1042 left that view and its list row became `picked-up`.

On this run date, window 7 includes H-1042 (18 days) and H-1102 (8 days). The 18 November 2026 acceptance example, where only H-1042 is overdue at window 7, is covered by the unit tests that inject that date.

## Known Limitations

Out of scope for KAN-3:

- Sending email or SMS.
- Connecting to the city library circulation system.
- Changing how a hold is marked picked up.
- Fines, renewals, and checkout.
- Replacing `GET /api/holds` or the existing list on `/`.

The code review also left these existing behaviors out of scope: pickup error text repeats the hold id (SEC-1), the existing pickup action does not report a network failure (EH-1), and the status strings `"ready"` and `"picked-up"` are not named constants (DRY-2). DRY-1, the duplicated table-row code in the page, is deferred. No shared helper was extracted.

Fields whose value is Not Found:

- A named timezone is Not Found. The decision is the server-local date. Day counts use that date and do not use a client clock.
- The stored string format of `readySince` is Not Found in the story. The accepted decision is ISO `YYYY-MM-DD`, which is how the seed stores it. A missing or unparseable value is left off the overdue list.
- The JSON name for days waiting is Not Found in the story. The accepted decision is `daysWaiting`.
- The JSON envelope of `GET /api/holds/overdue` is Not Found in the story. The accepted decision is `{ "windowDays", "holds" }`.
- The sort order is Not Found in the story. The accepted decision is the longest wait first, then `id` ascending.
- The page control used to edit the window is Not Found in the story. The accepted decision is a number input that starts at 7, plus a button.
- Whether the long-waiting view replaces the full list is Not Found beyond the rule that the full list and pickup stay available. The accepted decision is a separate section below the existing list.
- Titles and patron details not stated in the story example are Not Found. H-1042's title is Not Found. H-1048's patron name is Not Found. The seed data supplies values the story does not.

## Reviewer Checklist

- [ ] Correctness — Does each component behave as specified in .cursor/artifacts/requirements-agent/requirements.md?
- [ ] Security — Are secrets excluded from output? Is user input validated?
- [ ] Error Handling — Are bad input, a missing hold, and an empty overdue list handled gracefully?
- [ ] Test Coverage — Do tests cover the happy path AND the 'Not Found' / missing-field edge cases?
- [ ] Code Clarity — Are function names self-explanatory? Is logic easy to follow without comments?
- [ ] DRY Principle — Is there duplicated logic that could be refactored into a shared function?
- [ ] Dependency Safety — Are any known-vulnerable package versions in use?
