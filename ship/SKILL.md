---
name: ship
description: Backs up and restores the /ship slash command (commit, push, close GitHub issue). Use when restoring or syncing ~/.claude/commands/ship.md, or after a machine reset.
---

# ship: Personal Slash Command Backup & Restore

Backup and restore mechanism for your `/ship` slash command that automates the final step of your issue-driven development workflow: commit completed work → push → comment on and close the related GitHub issue.

## The /ship Workflow

When you invoke `/ship` in Claude Code:

1. **Inspect changes** — examine what's staged and unstaged via `git status` and `git diff`
2. **Stage specific files** — add only the files belonging to the completed unit of work (no `git add -A` or broad sweeps)
3. **Create commit** — with a concise message ending in the standard co-author line
4. **Push** — to the current branch's remote (or establish upstream if needed)
5. **Comment on issue** — post a Thai-language summary to the GitHub issue (files, commit hash, push confirmation)
6. **Close issue** — if still open (or note if already auto-closed per your convention)
7. **Report back** — brief confirmation of commit hash, push result, issue URL

This ties together the `Note` persona's issue-filing discipline with safe git practices (no force-push, no broad staging, never amend).

## Restore and Sync

Replace `<skill-path>` with the absolute path to this `ship/` directory.

- **Restore** after a machine reset: `mkdir -p ~/.claude/commands && cp <skill-path>/commands/ship.md ~/.claude/commands/`, then start a new Claude Code session (commands are scanned at startup).
- **Sync** after editing `~/.claude/commands/ship.md`: `cp ~/.claude/commands/ship.md <skill-path>/commands/ship.md`, then commit `ship/commands/ship.md` in `my-skills`.
- Needs `gh` authenticated and an `origin` remote. This skill does not set them up.

Full restore steps, prerequisites, backup maintenance, and troubleshooting: [references/restore.md](references/restore.md)
