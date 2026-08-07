---
name: claude-code-skills-backup
description: Backup and restore the complete Claude Code skills library (~105 skills, ~6.4MB). Restores all skill content files from ~/.agents/skills/ and reconstructs the ~/.claude/skills/ symlink farm after a machine reset.
---

# claude-code-skills-backup: Complete Skills Library Backup & Restore

Backup and restore mechanism for your entire Claude Code skills library. On a fresh machine, this skill lets you instantly restore all ~105 skills without manual re-installation.

## What Is This?

This is a **living backup** of your complete Claude Code skills library:

- **~105 skills** installed across your development stack (Next.js, Go, Python, React, testing, databases, deployment, etc.)
- **6.4MB of content** representing months or years of curated expertise
- **Symlink architecture**: `~/.claude/skills/` is a farm of symlinks pointing to real content in `~/.agents/skills/`
- **This backup preserves the REAL files**, allowing both locations to be reconstructed after a machine reset or clean install

Without this backup, a machine reset loses all installed skills — you'd need to reinstall each one individually.

## Architecture

Claude Code uses a two-layer skill architecture:

```
~/.claude/skills/
├── ai-sdk -> ../../.agents/skills/ai-sdk          (symlink)
├── astro-framework-expert -> ../../.agents/skills/astro-framework-expert
├── go-fiber-v3 -> ../../.agents/skills/go-fiber-v3
... (100+ more symlinks)

~/.agents/skills/
├── ai-sdk/                                          (real files)
│   ├── README.md
│   ├── src/
│   └── ...
├── astro-framework-expert/
├── go-fiber-v3/
... (100+ more real skill folders)
```

This skill backs up the REAL files in `~/.agents/skills/` so you can reconstruct both the source files and the symlink layer after a reset.

## Restore Instructions

### Prerequisites

- Claude Code is installed and initialized (at least one session completed to create `~/.claude/` directory)
- You have this skill in your skills library: `/Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/`
- `~/.agents/` directory does not yet exist (or you're OK with overwriting old skill files)

### Step 1: Copy Skill Files to ~/.agents/skills/

```bash
mkdir -p ~/.agents/skills
cp -R /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills/* ~/.agents/skills/
```

This restores all 105+ real skill folders and their content to their canonical location.

### Step 2: Reconstruct the ~/.claude/skills/ Symlink Farm

```bash
mkdir -p ~/.claude/skills
for d in ~/.agents/skills/*/; do
  name=$(basename "$d")
  ln -sf "../../.agents/skills/$name" ~/.claude/skills/"$name"
done
```

This creates symlinks from `~/.claude/skills/` back to `~/.agents/skills/` for each skill, matching the original symlink targets.

### Verify Restoration

After both steps, verify the restore was successful:

```bash
# Should show ~105 symlinks
ls ~/.claude/skills | wc -l

# Should show ~105 symlinks
find ~/.claude/skills -maxdepth 1 -type l | wc -l

# Spot-check: verify one symlink target
ls -la ~/.claude/skills/ai-sdk
# Output should look like: lrwxr-xr-x ... ai-sdk -> ../../.agents/skills/ai-sdk

# Verify symlink actually points to real files
ls ~/.agents/skills/ai-sdk | head -5
# Should show SKILL.md, README.md, or other real files (not an error)
```

### Step 3: Start a New Claude Code Session

Skill discovery happens at session startup. After restoring the skill files and symlinks:

1. Close any running Claude Code windows or terminal sessions
2. Open a fresh Claude Code session in a new terminal
3. All 105+ skills should now be available for loading by persona configurations

## Important: Dependent Personas & Skills

Many of your persona configurations (stored in `~/.claude/agents/`) reference specific skills by name. After restoring this skills library, **re-restore your personas** using the `my-agent` skill if you haven't already:

1. Restore personas first (or at the same time):
   ```bash
   mkdir -p ~/.claude/agents
   cp /Users/taweechai/Documents/GitHub/my-skills/my-agent/agents/*.md ~/.claude/agents/
   ```

2. Then restore skills (this skill).

3. Then start a new Claude Code session.

**Restore order:** `my-agent` (personas) → this skill (skills library) → new session. Personas will automatically load the correct skills they reference.

If you restore this skill but not your personas, skills will be available but no persona will load them. The skills are useful standalone, but personas expect to reference them by name.

## Keeping This Backup Current

Skills are usually added by installing new skill packages or updating existing ones. Since skills are stored in `~/.agents/skills/` outside of git, this backup can become stale if you install new skills but don't sync them back into this folder.

### To Keep the Backup Current

Whenever you install a new skill package or update an existing skill:

1. Re-run the backup copy to sync new/updated skills:
   ```bash
   cp -R ~/.agents/skills/* /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills/
   ```

2. Commit the updated skills folder to your `my-skills` git repository:
   ```bash
   cd /Users/taweechai/Documents/GitHub/my-skills
   git add claude-code-skills-backup/skills/
   git commit -m "Update: sync latest skills library backup (~105 skills)"
   git push
   ```

**Frequency:** Monthly or after major skill installations is reasonable; daily if you actively develop new skills.

## Complete Restoration Suite

This skill pairs with others for a complete "restore my entire Claude Code setup":

| Skill | Scope | Restore Order |
|---|---|---|
| **my-agent** | Persona definitions (13 specialist + 1 global) | 1st |
| **claude-code-skills-backup** | Skills library (~105 skills, 6.4MB) | 1st or 2nd (parallel OK) |
| **ship** | Slash commands for Claude Code CLI | 3rd |

**Recommended restore order:**
1. `my-agent` and `claude-code-skills-backup` in parallel (no dependency between them)
2. `ship` last (lightweight, depends on both)

After all three, start a new Claude Code session and your entire multi-agent system, skills library, and CLI commands will be fully functional.

## Troubleshooting

### Skills not showing up after restore

1. **Did you copy all skills?** Run: `ls ~/.agents/skills/ | wc -l` — should be ~105.
2. **Did you create the symlinks?** Run: `ls ~/.claude/skills | wc -l` — should match ~/.agents/skills count.
3. **Are the symlinks correct?** Run: `ls -la ~/.claude/skills/ai-sdk` — should show `-> ../../.agents/skills/ai-sdk`.
4. **Did you start a NEW session?** Skill discovery happens at startup; a running session won't see new skills.

### Symlinks pointing to wrong location

If symlinks show `-> /Users/taweechai/.agents/skills/...` (absolute path) instead of `-> ../../.agents/skills/...` (relative path):

```bash
# Remove incorrect symlinks
rm ~/.claude/skills/*

# Recreate with correct relative paths
for d in ~/.agents/skills/*/; do
  name=$(basename "$d")
  ln -sf "../../.agents/skills/$name" ~/.claude/skills/"$name"
done
```

### Backup folder is huge / copy hung

If the copy command (`cp -R ...`) seems to be taking forever or the folder grows unexpectedly large:

1. **Stop the copy** (Ctrl+C)
2. **Check for symlink loops:**
   ```bash
   ls -la ~/.agents/skills/claude-code-skills-backup 2>&1 | head -5
   ```
   If `claude-code-skills-backup` already exists inside `~/.agents/skills/`, the copy recursed infinitely.
3. **Clean up and retry:**
   ```bash
   rm -rf /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills
   mkdir -p /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills
   cp -RL ~/.agents/skills/* /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills/
   ```
   Use `-L` (dereference all symlinks) to avoid issues.

### "Too many open files" during copy

macOS has a low default file descriptor limit. If you hit this during the copy:

```bash
# Temporarily raise limit
ulimit -n 4096

# Then re-run the copy
cp -RL ~/.agents/skills/* /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills/
```

## Summary

This skill is a **one-command + one-loop restore** for your entire skills library:

```bash
# Step 1: Copy skill files
mkdir -p ~/.agents/skills
cp -R /Users/taweechai/Documents/GitHub/my-skills/claude-code-skills-backup/skills/* ~/.agents/skills/

# Step 2: Create symlinks
mkdir -p ~/.claude/skills
for d in ~/.agents/skills/*/; do
  name=$(basename "$d")
  ln -sf "../../.agents/skills/$name" ~/.claude/skills/"$name"
done

# Step 3: Start a new Claude Code session
# All 105+ skills will be available
```

After that, your entire skills library is restored and ready for your personas to reference.

**Key point:** This backup is as good as the last time you synced `~/.agents/skills/` into this folder. Keep it current by re-copying new/updated skills before committing, and you'll always be one folder copy away from a complete recovery after a machine reset.
