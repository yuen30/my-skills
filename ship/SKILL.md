---
name: ship
description: Backup and restore the /ship slash command — commit + push + close GitHub issue workflow for issue-driven development
---

# ship: Personal Slash Command Backup & Restore

Backup and restore mechanism for your `/ship` slash command that automates the final step of your issue-driven development workflow: commit completed work → push → comment on and close the related GitHub issue.

## What Is This?

This is a **living backup** of your `/ship` command:

- **Slash command file**: `~/.claude/commands/ship.md` — defines the `/ship` action callable from Claude Code
- **Purpose**: Eliminate manual ceremony when finishing a unit of work tied to a GitHub issue (per your Note-persona convention)
- **Integration**: Works seamlessly with the issue-per-unit-of-work discipline where:
  - A Note persona files a Thai-language GitHub issue at the start of work
  - You complete the implementation, testing, verification
  - You run `/ship [issue-number]` to stage, commit, push, and auto-close the issue in one step
  - The issue thread gets a Thai comment with the commit hash and push confirmation

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

## Restore Instructions

### Prerequisites

- Claude Code is installed and initialized (at least one session completed to create `~/.claude/` directory)
- GitHub CLI (`gh`) is authenticated and configured
- You have this skill in your skills library: `/Users/taweechai/Documents/GitHub/my-skills/ship/`

### Step 1: Copy Command File

```bash
mkdir -p ~/.claude/commands
cp /Users/taweechai/Documents/GitHub/my-skills/ship/commands/ship.md ~/.claude/commands/
```

This restores the `/ship` command file to its canonical location.

### Step 2: Start a New Claude Code Session

Slash commands are scanned at session initialization. After copying the command file, open Claude Code in a fresh terminal window or close and reopen the existing session. The `/ship` command should now be available.

### Verify Restoration

List the restored commands:
```bash
ls -la ~/.claude/commands/
```

You should see at least:
```
ship.md
```

Try invoking the slash command in Claude Code:
```
/ship 123
/ship https://github.com/user/repo/issues/456
/ship
```

If the command autocompletes and prompts for the issue number, the restore was successful.

## Important Dependencies

The `/ship` command requires:

1. **GitHub CLI (`gh`)** — must be installed and authenticated (`gh auth login`)
2. **Git remote** — the current repo must have a `origin` remote (or appropriate named remote) pointing to a GitHub repository
3. **Issue-per-unit-of-work discipline** — your repository must follow the convention where:
   - A new GitHub issue is filed at the start of each task (typically by the Note persona in Thai)
   - The `/ship` command expects to find that issue by number/URL or will search for the most recent one
4. **Conventional commits** — your project should support or tolerate the standard commit message format with co-author metadata

These are **prerequisites your workflow must already provide** — this skill does not set them up itself.

## Keeping This Backup Current

When you edit the `/ship` command in `~/.claude/commands/ship.md` (to refine the workflow, add new steps, or handle edge cases), **re-copy that file into this skill folder** to keep the backup synchronized:

```bash
cp ~/.claude/commands/ship.md /Users/taweechai/Documents/GitHub/my-skills/ship/commands/ship.md
```

Then commit the updated file to your `my-skills` git repository:

```bash
cd /Users/taweechai/Documents/GitHub/my-skills
git add ship/commands/ship.md
git commit -m "update(ship): sync /ship command changes"
git push
```

## Pairing with my-agent

This skill works alongside the `my-agent` skill for a complete "restore my whole Claude Code setup" flow:

- **my-agent**: Restores all 13 specialist personas + khun-abe orchestrator to `~/.claude/agents/`
- **ship**: Restores the `/ship` slash command to `~/.claude/commands/`

Together, they recreate your entire Claude Code environment (agents + commands) on a fresh machine after `git clone my-skills && bun restore-all` (or equivalent).

## Troubleshooting

### /ship command not showing up after restore

1. Did you copy the file to `~/.claude/commands/ship.md`? Run: `ls ~/.claude/commands/` — you should see `ship.md`
2. Did you start a **new** Claude Code session? Session scans happen at startup; a running session won't pick up new commands.
3. Check Claude Code's version — ensure it supports the `/commands/` directory (recent versions only).

### /ship fails on commit step

- **Ambiguous diff**: Multiple unrelated pending changes mixed in the tree. The command will ask you to confirm the exact file list before staging. Provide a clear list of specific files.
- **No upstream branch**: If the current branch has no remote upstream, `/ship` will push with `-u origin <branch>` automatically.
- **Git hooks failing**: The command respects pre-commit hooks and will not skip them. Fix the underlying issue (lint, typecheck, etc.) before retrying.

### /ship fails to find the issue

- Provide the issue number or full GitHub URL explicitly: `/ship 123` or `/ship https://github.com/user/repo/issues/456`
- If no argument is given, the command searches for the most recent GitHub issue filed in this session (by the Note persona or manually). Ensure at least one relevant issue exists.

### Command not pushing or closing issue

- Verify `gh auth login` is completed: `gh auth status`
- Verify the git remote is correct: `git remote -v`
- Check that the target GitHub issue exists and you have permission to comment/close it

## Summary

This skill is a **one-command restore** for your `/ship` automation:

```bash
mkdir -p ~/.claude/commands && \
cp /Users/taweechai/Documents/GitHub/my-skills/ship/commands/ship.md ~/.claude/commands/
```

After that, restart Claude Code, and the `/ship` command is ready to use.

**Key point:** This backup is only as current as the last time you copied the command file into it. Keep it in sync by re-copying whenever you refine the `/ship` workflow locally, and commit those changes to your `my-skills` git repo.
