#!/usr/bin/env python3
"""sessionStart hook: report which Agentic SDLC artifacts exist."""

import json
import sys
from pathlib import Path

GATES = (
    (".cursor/artifacts/requirements-agent/requirements.md", "Step 1 — Requirements"),
    (".cursor/artifacts/architect/architecture.md", "Step 2 — Architecture"),
    (".cursor/artifacts/design-reviewer/design-review.md", "Step 3 — Design review"),
    (".cursor/artifacts/planner/impl-plan.md", "Step 4 — Implementation plan"),
)


def gate_report(root: Path) -> str:
    lines = ["Agentic SDLC gate status:"]
    next_step = None
    for filename, label in GATES:
        present = (root / filename).is_file()
        state = "present" if present else "missing"
        lines.append(f"- {label}: {state} ({filename})")
        if not present and next_step is None:
            next_step = label
    if next_step is None:
        lines.append(
            "Planning gates are present. Continue from the approved task in "
            ".cursor/artifacts/planner/impl-plan.md, then code review, "
            "verification, and the pull request."
        )
    else:
        lines.append(
            f"Next gate: {next_step}. Wait for human approval before advancing."
        )
    story = root / "docs" / "user-story.md"
    story_state = "present" if story.is_file() else "missing"
    lines.append(f"Story input: {story_state} (docs/user-story.md).")
    lines.append(
        "Story loader: python scripts/load_user_story.py "
        "(Jira, Confluence, Word, or file, set in config/jira.local.json)."
    )
    lines.append("Artifacts: .cursor/artifacts/<sub-agent>/, never the repository root.")
    lines.append("Procedure: .cursor/skills/agentic-sdlc/SKILL.md.")
    lines.append(
        "Orchestrator: the parent agent delegates one step, then waits for approval."
    )
    lines.append("Sub-agents: .cursor/agents/.")
    return "\n".join(lines)


def main() -> None:
    sys.stdin.read()
    report = gate_report(Path.cwd())
    json.dump({"additional_context": report}, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump({}, sys.stdout)
        sys.stdout.write("\n")
