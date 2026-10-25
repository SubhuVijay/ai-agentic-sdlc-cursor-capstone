---
name: agentic-sdlc
description: >-
  Drives the Agentic SDLC for Automated Documentation Sync: requirements,
  architecture, design review, implementation planning, implementation,
  code review, verification, and pull request. Use when the user mentions
  SDLC, the user story, requirements.md, architecture.md, design-review.md,
  impl-plan.md, implementation, code review, verification, changelog, or a
  pull request for this capstone.
---

# Agentic SDLC

The human approves each step. Finish the step, show the result, and wait. Commit only when the user asks.

## Pick the step

The active step is the first missing artifact, unless the user names a step.

| Step | Artifact | Guide |
| --- | --- | --- |
| 1 Requirements | `requirements.md` | [requirements.md](requirements.md) |
| 2 Architecture | `architecture.md` | [architecture.md](architecture.md) |
| 3 Design review | `design-review.md` | [design-review.md](design-review.md) |
| 4 Implementation plan | `impl-plan.md` | [impl-plan.md](impl-plan.md) |
| 5 Implementation | approved task in `src/` and `tests/` | [implementation.md](implementation.md) |
| 6 Code review | `code-review.md` | [review.md](review.md) |
| 7 Verify | `verification-report.md` | [verify.md](verify.md) |
| 8 Pull request | PR description and `CHANGELOG.md` | [pull-request.md](pull-request.md) |

Story input: `docs/user-story.md`. Prompt library: `prompts/`.

## Hard stops

- Do not write `requirements.md` until the user has answered the clarifying questions.
- Do not write production code before `impl-plan.md` exists and the user has named the task.
- Do not invent missing documentation facts. Record `Not Found`.
- Do not print secrets, `.env` values, tokens, or credential file contents.
- Do not skip a gate because a later prompt was pasted.
