---
name: agentic-sdlc
description: >-
  Drives the Agentic SDLC for the Lane Street Library hold shelf. The session
  agent is the orchestrator and delegates each step to a sub-agent:
  requirements, architecture, design review, implementation planning,
  implementation, code review, verification, and pull request. The story is
  loaded from Jira, Confluence, Word, or a local file. Use when the user
  mentions SDLC, the orchestrator, a sub-agent, Jira, the user story,
  requirements, architecture, design review, implementation plan,
  implementation, code review, verification, changelog, or a pull request
  for this hold shelf.
---

# Agentic SDLC

The session agent is the orchestrator. Sub-agents perform the steps. The human approves each handoff. Commit only when the user asks.

## Orchestrator

The parent chat delegates. It does not write the step's artifact or product code itself. It may read files to show the user what a sub-agent wrote.

1. Pick the active step from the table below.
2. Call that one sub-agent. Pass a brief it can act on, because it cannot see this chat. Include the step, the procedure path, the approved artifact paths, and the user's latest answers, decisions, or named task.
3. Wait for the handoff. Show it to the user. Stop.
4. When the user continues the same step, resume that sub-agent and pass the new message.
5. Start the next sub-agent only after the user approves the current step.

Run one SDLC sub-agent at a time. Do not run the next step in parallel. Sub-agents do not launch another SDLC sub-agent.

## Handoff

Each sub-agent returns only this block:

```text
step: <number>
agent: <sub-agent name>
status: waiting | done | blocked
artifact: <path or none>
summary: <what was done or asked>
questions: <numbered questions, or none>
blockers: <what stopped the step, or none>
```

`waiting` means the orchestrator asks those questions and does not call the next agent. `done` means the orchestrator shows the summary and waits for approval. `blocked` means the orchestrator reports the blocker and stops.

## Pick the step

The active step is the first missing artifact, unless the user names a step. Delegate it to the sub-agent in this table.

| Step | Sub-agent | Artifact | Guide |
| --- | --- | --- | --- |
| 1 Requirements | `requirements-agent` | `.cursor/artifacts/requirements-agent/requirements.md` | [requirements.md](requirements.md) |
| 2 Architecture | `architect` | `.cursor/artifacts/architect/architecture.md` | [architecture.md](architecture.md) |
| 3 Design review | `design-reviewer` | `.cursor/artifacts/design-reviewer/design-review.md` | [design-review.md](design-review.md) |
| 4 Implementation plan | `planner` | `.cursor/artifacts/planner/impl-plan.md` | [impl-plan.md](impl-plan.md) |
| 5 Implementation | `implementer` | approved task in `src/holdshelf` and `tests/` | [implementation.md](implementation.md) |
| 6 Code review | `code-reviewer` | `.cursor/artifacts/code-reviewer/code-review.md` | [review.md](review.md) |
| 7 Verify | `verifier` | `.cursor/artifacts/verifier/verification-report.md` | [verify.md](verify.md) |
| 8 Pull request | `release-agent` | `.cursor/artifacts/release-agent/pull-request.md` and `CHANGELOG.md` | [pull-request.md](pull-request.md) |

## Artifact folders

Each sub-agent writes its markdown only in `.cursor/artifacts/<sub-agent>/`, and creates that folder when it first writes the file. Step markdown is never written at the repository root, and a root-level copy does not pass a gate. `CHANGELOG.md` stays at the repository root. The implementer writes code, not a markdown artifact.

## Story input

The story source is set in `config/jira.local.json`, copied from `config/jira.example.json`. `source` is `jira`, `confluence`, `word`, or `file`. `python scripts/load_user_story.py` writes the story to `docs/user-story.md`. With no local config, the existing `docs/user-story.md` is used. Never open or print `config/jira.local.json`. The script reads it.

Prompt library: `prompts/`.

## Hard stops

- Do not write step markdown at the repository root. Use that sub-agent's folder under `.cursor/artifacts/`.
- Do not write `.cursor/artifacts/requirements-agent/requirements.md` until the user has answered the clarifying questions.
- Do not write production code before `.cursor/artifacts/planner/impl-plan.md` exists and the user has named the task.
- Do not invent missing facts. Record `Not Found`.
- Do not print secrets, `.env` values, tokens, `config/jira.local.json`, or credential file contents.
- Do not skip a gate because a later prompt was pasted.
- Do not perform a step in the parent chat. Delegate it to that step's sub-agent.
- Do not start the next sub-agent before the user approves the current handoff.
