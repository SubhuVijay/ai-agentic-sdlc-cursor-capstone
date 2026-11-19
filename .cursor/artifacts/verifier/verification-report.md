# Verification report — KAN-3

**Story:** KAN-3, Show holds that have waited past the pickup window
**Result:** pass
**Run date:** 20 November 2026 (server-local date on the machine that served the app)
**Scope:** T1 to T4. No product code was changed. DRY-1 and the deferred notes were left as recorded in the code review.

## Command

```text
python -m unittest discover -s tests -v
```

Exit code: 0. Ran 65 tests in 0.190s. Result: OK.

Hook tests, story-loader tests, and hold-shelf tests ran in this same command.

## Test output

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

The 18 November 2026 acceptance examples are covered by the unit tests that inject that date, including `test_seed_window_7_returns_only_the_sixteen_day_hold` and `test_omitted_window_returns_the_sixteen_day_hold`. A missing `readySince` is covered by `test_missing_ready_since_is_excluded` and `test_missing_or_unparseable_ready_since_is_excluded`. The live seed has a `readySince` on every hold, so the running server has no such row to exclude.

## Run date and expected counts

The app was started with `PYTHONPATH=src` and `python -m holdshelf`, which serves http://127.0.0.1:8765. The server-local date was 20 November 2026. Calendar days from each seed `readySince` to that date:

| Hold | Ready since | Days waiting | On the overdue list at window 7 |
| --- | --- | --- | --- |
| H-1042 | 2026-11-02 | 18 | yes |
| H-1102 | 2026-11-12 | 8 | yes |
| H-1048 | 2026-11-16 | 4 | no |
| H-0991 | 2026-10-28 | 23 | no, status is `picked-up` |

On the story example date, 18 November 2026, H-1042 had waited 16 days and was the only overdue hold at window 7. H-1102 had waited 6 days. Two days later H-1102 has waited 8 days, so a 7-day window includes both H-1042 and H-1102. That difference is the one DR-14 says to expect.

## API check

Checked against the running server before any pickup of a ready hold.

- `GET /api/holds` returned 200 and the four seed holds, in shelf order, with `id`, `title`, `patron`, `readySince`, `status`, and `phone`. H-1048's phone was JSON `null`. The three ready holds were `ready`. H-0991 was `picked-up`.
- `GET /api/holds?windowDays=abc` returned 200 and the same list.
- `GET /api/holds/overdue` with `windowDays` omitted returned 200, `windowDays` 7, and holds H-1042 (18 days, phone `555-0142`) then H-1102 (8 days, phone `555-0177`).
- `GET /api/holds/overdue?windowDays=7` returned the same window and the same holds.
- `GET /api/holds/overdue?windowDays=1` returned 200, `windowDays` 1, and H-1042 (18), H-1102 (8), H-1048 (4). H-1048's phone was JSON `null`. The body did not contain the text `Not Found`.
- A window equal to a ready hold's wait left that hold out: `windowDays=4` left out H-1048, `windowDays=8` left out H-1102, and `windowDays=18` left out H-1042. H-0991 stayed out of every overdue result.
- `GET /api/holds/overdue?windowDays=3650` returned 200, `windowDays` 3650, and `holds` `[]`.
- These bad windows each returned 400 with body `{"error": "windowDays must be a whole number of days from 1 to 3650."}` and no `holds` key: `abc`, an empty `windowDays=`, `0`, `-1`, `7.5`, `7.0`, and `3651`. The body did not repeat the rejected value.
- `POST /api/holds/H-0000/pickup` returned 404. `POST /api/holds/H-0991/pickup` returned 409. The shelf list was unchanged after both.

## Browser check

The Playwright browser tool was unavailable. The page was opened in headless Chrome and the controls were clicked. This was the real page at http://127.0.0.1:8765/, not a separate copy of the HTML.

- The existing list loaded four rows. Headers were Hold, Title, Patron, Ready since, Status, and a blank action column. Ready rows had **Mark picked up**. H-0991 showed `picked-up` and had no button. That table did not show a phone, `Not Found`, or days waiting.
- **Show long-waiting holds** at window 7 rendered H-1042 with 18 days and `555-0142`, then H-1102 with 8 days and `555-0177`.
- Window 1 added H-1048, Braiding Sweetgrass, Luis Ortega, ready since 2026-11-16, 4 days, phone `Not Found`.
- Window 3650 rendered the single cell `No ready hold is past the pickup window.`
- A filled long-waiting table was then requested again, and each bad value cleared that table and showed the fixed message `windowDays must be a whole number of days from 1 to 3650.` Values checked in the page: `abc`, empty, `0`, `-1`, `7.5`, and `3651`. The number input cannot hold `abc`, so the control's value became empty and the page submitted an empty `windowDays`. The server still returned the fixed 400 message, and the table was cleared. The direct HTTP request `windowDays=abc` is the non-numeric check recorded above.
- The **Show long-waiting holds** button was disabled while each overdue request was in flight. The check read that state inside `fetch`, before the response returned: 17 samples, all `true`. The button was enabled again when each request finished.
- After a successful window of 1, the input was changed to 3650 and **Show long-waiting holds** was not clicked. **Mark picked up** on H-1042 then refreshed the long-waiting view from `/api/holds/overdue?windowDays=1`. The table showed H-1102 (8 days, `555-0177`) and H-1048 (4 days, `Not Found`). H-1042's list row became `picked-up` and the pickup button was gone.
- A following API read confirmed H-1042 was `picked-up` and `windowDays=1` returned H-1102 then H-1048.

## Secrets

The page HTML, the 400 error bodies, and the rendered page text were checked for token and credential markers. None were present. This report does not quote a token, a `.env` value, or `config/jira.local.json`. That file was not opened. The test output's line `No config/jira.local.json. Using docs/user-story.md` is the story loader's usual message when the local config is absent.

## Content-quality failures

None.

## Assumptions

- Day counts use the server-local date 20 November 2026 and whole calendar days, as NFR-1 requires.
- AC-1's 16-day example stays with the unit tests that pin the date at 18 November 2026. The live check uses the counts in the table above.
- The live seed cannot demonstrate a missing `readySince`. Those exclusions are the passing unit tests named above.
