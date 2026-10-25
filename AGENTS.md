# Agent instructions

This repository delivers Automated Documentation Sync through an Agentic SDLC. Follow the `agentic-sdlc` skill for the active step.

## Order

1. Read `docs/user-story.md`, clarify with the user, then write `requirements.md`.
2. Write `architecture.md` from the approved requirements.
3. Review that architecture, write `design-review.md`, and update `architecture.md` with agreed changes.
4. Write `impl-plan.md` in dependency order, including tasks that are blocked.
5. Implement only the task the user approved. Code goes in `src/`. Tests go in `tests/`.
6. Write `code-review.md` using the review checklist in the skill.
7. Run tests and a content check. Write `verification-report.md`.
8. When asked, update `CHANGELOG.md` and open a pull request whose description has Summary, Changes Made, Test Evidence, Known Limitations, and Reviewer Checklist.

## Gates

- Ask clarifying questions and wait for answers before writing `requirements.md`.
- Do not start a later step while an earlier artifact is missing.
- Do not write production code before `impl-plan.md` exists and the user names the task.
- Record unknown facts as `Not Found`.
- Do not print secrets, tokens, `.env` values, or credential-file contents.
- Commit, push, and open a pull request only when the user asks.

## Inputs

- Story: `docs/user-story.md`
- Prompts: `prompts/`
- Procedures: `.cursor/skills/agentic-sdlc/`
