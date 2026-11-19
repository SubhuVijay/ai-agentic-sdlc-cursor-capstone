# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Retargeted the workspace to the Lane Street Library hold shelf (HOLD-21), with the baseline hold-shelf app in `src/holdshelf`.
- Each sub-agent writes its markdown under `.cursor/artifacts/<sub-agent>/` instead of the repository root.

### Added

- `scripts/load_user_story.py` and `config/jira.example.json` load the story from Jira, Confluence, Word, or a local file into `docs/user-story.md`.
- Hooks block reads of `config/jira.local.json`.

## [0.1.0] - 2026-10-25

### Added

- Agentic SDLC workspace for the Lane Street Library hold shelf: agent instructions, prompts, skill, rules, and hooks.
- Hook tests for the SDLC status report, destructive-command guard, and secret-file guard.
