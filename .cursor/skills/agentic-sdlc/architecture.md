# Step 2 — Architecture

Prerequisite: the user has approved `.cursor/artifacts/requirements-agent/requirements.md`.

1. Recommend an architecture that satisfies `.cursor/artifacts/requirements-agent/requirements.md` only. It extends the existing app in `src/holdshelf`. Include:
   - A mermaid component diagram
   - Each component and its responsibility
   - The technology choice and why it fits the requirements
   - Data flow from the librarian's action to the API response and the page
   - Where secrets and patron phone numbers are kept out of logs
2. Create `.cursor/artifacts/architect/` if needed and write that recommendation to `.cursor/artifacts/architect/architecture.md`. Do not write it at the repository root.
3. List assumptions in their own section. Wait for the user to accept or change them.
