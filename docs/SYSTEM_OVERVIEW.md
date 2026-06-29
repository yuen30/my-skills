# System Overview

## Repository

`my-skills` is a personal skill collection for agent workflows. The repo exposes a root `index.json` and one `SKILL.md` per skill folder.

## Installation

The documented install command is:

```bash
npx skills add yuen30/my-skills
```

For updating already installed global skills, use:

```bash
npx skills update -g -y
```

## Key Files

- `README.md`: Public overview and install command.
- `index.json`: Skill package index used by skill tooling.
- `<skill>/SKILL.md`: Individual skill instructions.
- `.ai-history.md`: Session handover log.
- `docs/YYYY-MM-DD.html`: Daily execution dashboard.

## Operational Notes

- Keep changes scoped to skill folders or docs related to the requested task.
- Prefer `npx skills update -g -y` for global updates.
- Use `npx skills add yuen30/my-skills -g --all` only when a fresh global install is required.
- Restart Codex after install/update so new skill metadata is loaded.
