# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Long-waiting holds for KAN-3. The hold shelf page lists ready holds that have waited strictly longer than the pickup window, with the days waiting and the patron phone. A missing phone is JSON `null` in the API and `Not Found` on that view.
- `GET /api/holds/overdue` accepts `windowDays`. An omitted value is 7. A whole number from 1 to 3650 is accepted. Any other value returns 400 with no hold list. Day counts use the server-local date.
- `scripts/load_user_story.py` and `config/jira.example.json` load the story from Jira, Confluence, Word, or a local file into `docs/user-story.md`.
- Hooks block reads of `config/jira.local.json`.

### Changed

- The existing hold list and pickup action stay in place. The long-waiting view is a separate section on the same page.
- Retargeted the workspace to the Lane Street Library hold shelf (HOLD-21), with the baseline hold-shelf app in `src/holdshelf`.
- Each sub-agent writes its markdown under `.cursor/artifacts/<sub-agent>/` instead of the repository root.

### Fixed

- Secret-file checks split both `\` and `/`, so a Windows path such as `C:\repo\.env` is blocked on Linux as well as Windows.

## [0.1.0] - 2026-10-25

### Added

- Agentic SDLC workspace for the Lane Street Library hold shelf: agent instructions, prompts, skill, rules, and hooks.
- Hook tests for the SDLC status report, destructive-command guard, and secret-file guard.
