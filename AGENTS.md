# Agent instructions

This repository delivers the Lane Street Library hold shelf story through an Agentic SDLC. The sample app in `src/holdshelf` already lists holds and marks them picked up. The story adds the long-waiting holds view on top of it. This chat is the orchestrator. Follow the `agentic-sdlc` skill for the active step, and delegate that step to the matching sub-agent.

## Order

Each sub-agent writes its markdown in its own folder under `.cursor/artifacts/`. Never at the repository root.

1. Load the story with `python scripts/load_user_story.py` (Jira, Confluence, Word, or file), read `docs/user-story.md`, clarify with the user, then write `.cursor/artifacts/requirements-agent/requirements.md`.
2. Write `.cursor/artifacts/architect/architecture.md` from the approved requirements.
3. Review that architecture, write `.cursor/artifacts/design-reviewer/design-review.md`, and update the architecture with agreed changes.
4. Write `.cursor/artifacts/planner/impl-plan.md` in dependency order, including tasks that are blocked.
5. Implement only the task the user approved. Extend `src/holdshelf`. Tests go in `tests/`.
6. Write `.cursor/artifacts/code-reviewer/code-review.md` using the review checklist in the skill.
7. Run tests and check the hold shelf against the requirements. Write `.cursor/artifacts/verifier/verification-report.md`.
8. When asked, update `CHANGELOG.md`, write `.cursor/artifacts/release-agent/pull-request.md`, and open a pull request whose description has Summary, Changes Made, Test Evidence, Known Limitations, and Reviewer Checklist.

## Gates

- Ask clarifying questions and wait for answers before writing the requirements.
- Do not start a later step while an earlier artifact is missing.
- Do not write production code before `.cursor/artifacts/planner/impl-plan.md` exists and the user names the task. Do not replace the existing list or pickup action.
- Record unknown facts as `Not Found`.
- Do not print secrets, tokens, `.env` values, `config/jira.local.json`, or credential-file contents.
- Commit, push, and open a pull request only when the user asks.

## Roles

The orchestrator sends one brief, reads the handoff, shows it to the user, and waits. A sub-agent performs that step and returns the handoff. It does not start the next step and it does not speak past the orchestrator.

| Step | Sub-agent | Artifact folder |
| --- | --- | --- |
| 1 Requirements | `requirements-agent` | `.cursor/artifacts/requirements-agent/` |
| 2 Architecture | `architect` | `.cursor/artifacts/architect/` |
| 3 Design review | `design-reviewer` | `.cursor/artifacts/design-reviewer/` |
| 4 Implementation plan | `planner` | `.cursor/artifacts/planner/` |
| 5 Implementation | `implementer` | none — code in `src/holdshelf` and `tests/` |
| 6 Code review | `code-reviewer` | `.cursor/artifacts/code-reviewer/` |
| 7 Verify | `verifier` | `.cursor/artifacts/verifier/` |
| 8 Pull request | `release-agent` | `.cursor/artifacts/release-agent/` |

The handoff format and the delegation rules are in `.cursor/skills/agentic-sdlc/SKILL.md`.

## Inputs

- Story: `docs/user-story.md`, loaded by `scripts/load_user_story.py` from the source in `config/jira.local.json`
- Story source template: `config/jira.example.json`
- Prompts: `prompts/`
- Procedures: `.cursor/skills/agentic-sdlc/`
- Sub-agents: `.cursor/agents/`
- Artifacts: `.cursor/artifacts/`
