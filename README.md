# Agentic SDLC Capstone — Lane Street Library hold shelf

This repository is the Cursor workspace for the Lane Street Library hold shelf. Cursor agents run the delivery lifecycle. The sample application in `src/holdshelf` is the desk tool already in use. The story adds the long-waiting holds view on top of it, after requirements, architecture, design review, and the implementation plan are approved.

## What you practice

Each step is a gated conversation with the agent. The story is pulled from Jira (or Confluence, Word, or a local file). The human answers questions, approves artifacts, and decides when to commit or open a pull request.

| Step | Sub-agent | Outcome | How to start |
| --- | --- | --- | --- |
| 1. Requirements | `requirements-agent` | `.cursor/artifacts/requirements-agent/requirements.md` | [prompts/01-requirements.md](prompts/01-requirements.md) |
| 2. Architecture | `architect` | `.cursor/artifacts/architect/architecture.md` | [prompts/02-architecture.md](prompts/02-architecture.md) |
| 3. Design review | `design-reviewer` | `.cursor/artifacts/design-reviewer/design-review.md` | [prompts/03-design-review.md](prompts/03-design-review.md) |
| 4. Implementation plan | `planner` | `.cursor/artifacts/planner/impl-plan.md` | [prompts/04-implementation-plan.md](prompts/04-implementation-plan.md) |
| 5. Implementation | `implementer` | Code under `src/holdshelf` and `tests/` | [prompts/05-implementation.md](prompts/05-implementation.md) |
| 6. Review | `code-reviewer` | `.cursor/artifacts/code-reviewer/code-review.md` | [prompts/06-code-review.md](prompts/06-code-review.md) |
| 7. Verify | `verifier` | `.cursor/artifacts/verifier/verification-report.md` | [prompts/07-verify.md](prompts/07-verify.md) |
| 8. Pull request | `release-agent` | `.cursor/artifacts/release-agent/pull-request.md` and `CHANGELOG.md` | [prompts/08-pull-request.md](prompts/08-pull-request.md) |

Each sub-agent writes its markdown under `.cursor/artifacts/<sub-agent>/`, never at the repository root. Those folders are created when a step first writes its file. `CHANGELOG.md` stays at the repository root.

## Load the story from Jira

1. Copy `config/jira.example.json` to `config/jira.local.json`. The local file is gitignored, and the hooks block agents from reading it.
2. Set `source` to `jira` and fill in `baseUrl`, `email`, `apiToken`, and `issueKey` (for example `HOLD-21`). Create the API token at [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens).
3. Run Step 1. The `requirements-agent` runs `python scripts/load_user_story.py`, which writes the issue to `docs/user-story.md` without printing the token.

`source` can also be `confluence` (a page id), `word` (a `.docx` path), or `file`. A Word document can be loaded directly with `python scripts/load_user_story.py --word docs/incoming/user-story.docx`. Without `config/jira.local.json`, the story already in [docs/user-story.md](docs/user-story.md) is used.

## Agent surface

| Exercise concept | Where it lives |
| --- | --- |
| Orchestrator | This chat, instructed by [AGENTS.md](AGENTS.md) and [.cursor/rules/orchestrator.mdc](.cursor/rules/orchestrator.mdc) |
| Sub-agents | [.cursor/agents](.cursor/agents) |
| Artifacts | `.cursor/artifacts/<sub-agent>/` |
| Instructions | [.cursor/rules](.cursor/rules) |
| Prompts | [prompts](prompts) |
| Skills | [.cursor/skills/agentic-sdlc](.cursor/skills/agentic-sdlc) |
| Hooks | [.cursor/hooks.json](.cursor/hooks.json) |
| Story loader | [scripts/load_user_story.py](scripts/load_user_story.py) and [config/jira.example.json](config/jira.example.json) |

Open a new Agent chat and paste the prompt for the step you are on, or ask to run that step. That chat is the orchestrator. It delegates the step to the sub-agent in `.cursor/agents/`, shows you the handoff, and waits for approval before the next step. The `agentic-sdlc` skill is the procedure. Prompts only select the step.

## Layout

```text
AGENTS.md                 Orchestrator contract for every session
docs/user-story.md        Incoming story (Step 1 input), written by the loader
config/jira.example.json  Story source template (Jira, Confluence, Word, or file)
scripts/load_user_story.py Loads that source into docs/user-story.md
prompts/                  One prompt per SDLC step
.cursor/agents/           Sub-agents that perform each step
.cursor/artifacts/        Markdown each sub-agent writes, one folder per sub-agent
.cursor/rules/            Persistent instructions
.cursor/skills/           Step procedures and handoff format
.cursor/hooks.json        Session context, shell guard, secret-file guard
src/holdshelf/            Sample app: list holds and mark them picked up
tests/                    Hook, story-loader, and hold-shelf tests
```

Run the sample app, then open http://127.0.0.1:8765 :

```bash
PYTHONPATH=src python -m holdshelf
```

On PowerShell: `$env:PYTHONPATH = "src"; python -m holdshelf`

The overdue API and the "waiting too long" view are not in the app yet. Step 5 adds them after the story is approved.

## Hooks

Project hooks load when this folder is a trusted Cursor workspace.

| Hook | Behavior |
| --- | --- |
| `sessionStart` | Reports which SDLC artifacts exist under `.cursor/artifacts/`, which gate is next, and how the story is loaded |
| `beforeShellExecution` | Asks before force-push, `git reset --hard`, and forced `git clean`; blocks commands that print `.env`, `config/jira.local.json`, or the environment |
| `beforeReadFile` | Blocks reads of `.env` (except `.env.example` and `.env.sample`), `config/jira.local.json`, keys, and credential files |

Hooks call `python` and use the standard library only. If `python` is not on `PATH`, Cursor logs the failure and continues (fail-open) so a missing interpreter does not freeze the session.

## Checks

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same command on pull requests. See [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Prerequisites

- Cursor, with this folder opened as the workspace
- Git, and the GitHub CLI (`gh`) if Step 8 should open the pull request from the terminal
- Python 3.9 or newer, available as `python`
- A Jira Cloud API token, if the story is loaded from Jira

## Working agreement

- The orchestrator delegates one step to a sub-agent, shows the handoff, and waits before the next step. Requirements are not written until you answer the clarifying questions.
- A missing patron phone on the long-waiting view is recorded as `Not Found`. Missing facts are not guessed.
- Secrets stay out of chat, logs, commits, and generated docs. The Jira token lives only in `config/jira.local.json`.
- Commits and pull requests happen when you ask for them.
