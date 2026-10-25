# Agentic SDLC Capstone — Automated Documentation Sync

This repository is the workspace for the Automated Documentation Sync capstone. Cursor agents run the delivery lifecycle. The product code is added only after requirements, architecture, design review, and the implementation plan are approved.

## What you practice

Each step is a gated conversation with the agent. The human answers questions, approves artifacts, and decides when to commit or open a pull request.

| Step | Outcome | How to start |
| --- | --- | --- |
| 1. Requirements | `requirements.md` | [prompts/01-requirements.md](prompts/01-requirements.md) |
| 2. Architecture | `architecture.md` | [prompts/02-architecture.md](prompts/02-architecture.md) |
| 3. Design review | `design-review.md` | [prompts/03-design-review.md](prompts/03-design-review.md) |
| 4. Implementation plan | `impl-plan.md` | [prompts/04-implementation-plan.md](prompts/04-implementation-plan.md) |
| 5. Implementation | Code under `src/` and `tests/` | [prompts/05-implementation.md](prompts/05-implementation.md) |
| 6. Review | `code-review.md` | [prompts/06-code-review.md](prompts/06-code-review.md) |
| 7. Verify | `verification-report.md` | [prompts/07-verify.md](prompts/07-verify.md) |
| 8. Pull request | PR description, changelog, checklist | [prompts/08-pull-request.md](prompts/08-pull-request.md) |

The incoming story is [docs/user-story.md](docs/user-story.md). It is the source for Step 1, not the approved requirements.

## Agent surface

| Exercise concept | Where it lives |
| --- | --- |
| Agents | [AGENTS.md](AGENTS.md) |
| Instructions | [.cursor/rules](.cursor/rules) |
| Prompts | [prompts](prompts) |
| Skills | [.cursor/skills/agentic-sdlc](.cursor/skills/agentic-sdlc) |
| Hooks | [.cursor/hooks.json](.cursor/hooks.json) |

Open a new Agent chat and paste the prompt for the step you are on, or ask to run that step. The `agentic-sdlc` skill is the procedure. Prompts only select the step.

## Layout

```text
AGENTS.md                 Agent contract for every session
docs/user-story.md        Incoming story (Step 1 input)
prompts/                  One prompt per SDLC step
.cursor/rules/            Persistent instructions
.cursor/skills/           Step procedures
.cursor/hooks.json        Session context, shell guard, secret-file guard
src/                      Application code (Step 5)
tests/                    Hook tests now; product tests from Step 5
```

Planning artifacts (`requirements.md`, `architecture.md`, `design-review.md`, `impl-plan.md`) are created at the repository root during the exercise. They are intentionally absent until the matching step is approved.

## Hooks

Project hooks load when this folder is a trusted Cursor workspace.

| Hook | Behavior |
| --- | --- |
| `sessionStart` | Reports which SDLC artifacts exist and which gate is next |
| `beforeShellExecution` | Asks before force-push, `git reset --hard`, and forced `git clean`; blocks commands that print `.env` files or the environment |
| `beforeReadFile` | Blocks reads of `.env` (except `.env.example` and `.env.sample`), keys, and credential files |

Hooks call `python` and use the standard library only. If `python` is not on `PATH`, Cursor logs the failure and continues (fail-open) so a missing interpreter does not freeze the session.

## Checks

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same command on pull requests. See [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Prerequisites

- Cursor, with this folder opened as the workspace
- Git
- Python 3.9 or newer, available as `python`

## Working agreement

- The agent asks, then waits, before writing requirements or moving to the next step.
- Missing documentation facts are recorded as `Not Found`. They are not guessed.
- Secrets stay out of chat, logs, commits, and generated docs.
- Commits and pull requests happen when you ask for them.
