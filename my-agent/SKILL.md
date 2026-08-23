---
name: my-agent
description: Backup and restore three persona systems (Claude Code subagents 14-file set in ~/.claude/agents/, Codex CLI persona config in ~/.codex/AGENTS.md and ~/.agents/agents/AGENTS.md, and opencode persona config in ~/.config/opencode/) after a machine reset.
---

# my-agent: Personal Persona Backup & Restore

Backup and restore mechanism for three complementary persona systems:

1. **Claude Code subagents**: 13 specialist personas (Boss, Art, Boy, Toey, Oat, Keng, Joy, Safe, Poo, Note, Nine, Fah, Bank) plus the khun-abe global orchestrator
2. **Codex CLI persona config**: Single unified persona configuration file powering alternative CLI agent system
3. **opencode persona config**: Persona system for opencode editor with per-persona YAML configuration

On a fresh machine, this skill lets you instantly restore all persona definitions without manual recreation.

## What Is This?

This is a **living backup** of your multi-agent development system across two distinct platforms:

### Claude Code Subagents (14-file system in `~/.claude/agents/`)

- **13 specialist personas**: Each handles a distinct domain (UI, backend, testing, database, i18n, auth, analytics, documentation, mobile, production reliability, ML pipelines).
- **1 global catch-all**: `khun-abe` is the entry point for unspecialized or cross-cutting work.
- **Per-persona configuration**: Each persona is defined as a `~/.claude/agents/<name>.md` file with:
  - **Frontmatter**: name, description, tools list, model tier (opus/sonnet/haiku)
  - **Skills section**: list of loaded skills (from `~/.claude/skills/`)
  - **Workflow section**: persona-specific operating rules
  - **Global rules section**: inherited from `~/.claude/CLAUDE.md`

### Codex CLI Persona Config (single unified file)

- **Location**: `~/.codex/AGENTS.md` and `~/.agents/agents/AGENTS.md` (kept in sync — both locations must always contain identical content)
- **Format**: Single consolidated config file (not per-persona) with frontmatter (`alwaysApply: true`) and full persona definitions
- **Model naming**: Uses `gpt-5.6-sol`, `gpt-5.6-terra` naming (different from Claude's opus/sonnet/haiku)
- **Purpose**: Powers the Codex CLI persona system with same persona definitions in a different format

### opencode Persona Config (per-persona YAML files)

- **Location**: `~/.config/opencode/AGENTS.md` (unified orchestrator) and `~/.config/opencode/agents/*.md` (per-persona definitions)
- **Format**: Central AGENTS.md file with all personas listed + separate `.md` files for each persona with YAML frontmatter (description, mode: subagent, color: #hex, permission: {edit, bash})
- **Structure**: 13 core personas (art, boy, joy, keng, note, oat, poo, safe, toey, nine, fah, bank) plus 3 cavecrew helper subagents
- **Purpose**: Powers the opencode editor's persona switching with role-specific instructions and visual identity (color coding)

## Persona Roster

| Persona | Emoji | Scope | Model |
|---|---|---|---|
| Boss | 👑 | Architecture, scope, stability, coordination | opus |
| Art | 🎨 | UI/UX, accessibility, Tailwind, shadcn/ui | sonnet |
| Boy | ⚙️ | Backend, business logic, integrations | sonnet |
| Toey | 🧪 | Tests, lint, typecheck, build | haiku |
| Oat | 🐳 | Docker, CI/CD, deployment, observability | sonnet |
| Keng | 💾 | Database, ORM, safe migrations | opus |
| Joy | 🌐 | i18n, locale routing, translations | haiku |
| Safe | 🛡️ | Auth, authorization, secrets, OWASP | opus |
| Poo | 📊 | ETL, analytics, reports, performance | sonnet |
| Note | 📄 | API docs, runbooks, handover notes | haiku |
| Nine | 📱 | Mobile app development (iOS/Android, React Native) | sonnet |
| Fah | 🚨 | Production reliability, incident response, on-call | opus |
| Bank | 🤖 | Data engineering, ML pipelines | opus |
| khun-abe | (catch-all) | Global orchestrator / fallback agent | inherit |

## Restore Instructions

**Placeholder note:** In all command examples below, replace `<skill-path>` with the absolute local path to the directory containing this SKILL.md file (the `my-agent/` directory).

### Prerequisites

- Claude Code is installed and initialized (at least one session completed to create `~/.claude/` directory)
- You have this skill in your skills library (cloned to a local directory)

### Step 1: Copy Agent Files

```bash
mkdir -p ~/.claude/agents
cp <skill-path>/agents/*.md ~/.claude/agents/
```

This restores all 14 persona `.md` files to their canonical location.

### Step 2: Merge the Personas Table into ~/.claude/CLAUDE.md

Your fresh `~/.claude/CLAUDE.md` will already have a basic `## Personas` table (with default entries). Replace it with the one from this skill:

1. Open `<skill-path>/PERSONAS_TABLE.md` — copy the full table (both roster and model tiers sections).
2. Open `~/.claude/CLAUDE.md` — find the existing `## Personas` section and replace the entire table with the copied content.
3. Save.

Alternatively, if you want to preserve any other custom content in `~/.claude/CLAUDE.md`, just ensure the `## Personas` table matches the one in `PERSONAS_TABLE.md`.

### Step 3: Restore Codex CLI Persona Config

```bash
mkdir -p ~/.codex ~/.agents/agents
cp <skill-path>/codex/AGENTS.md ~/.codex/AGENTS.md
cp <skill-path>/codex/AGENTS.md ~/.agents/agents/AGENTS.md
```

This restores the Codex CLI persona configuration. **Important:** Both destination files (`~/.codex/AGENTS.md` and `~/.agents/agents/AGENTS.md`) must remain identical — Codex CLI reads from both locations interchangeably. If you edit one manually, you **must manually sync the other** to prevent configuration drift.

### Step 5: Restore opencode Persona Config

```bash
mkdir -p ~/.config/opencode/agents
cp <skill-path>/opencode/AGENTS.md ~/.config/opencode/AGENTS.md
cp <skill-path>/opencode/agents/*.md ~/.config/opencode/agents/
```

This restores the opencode persona configuration, including all 13 core personas and 3 cavecrew helper subagents with YAML metadata (color coding, permissions).

### Step 7: Start a New Claude Code Session

Claude Code configurations are scanned at session start. After restoring the persona files and updating `CLAUDE.md`, open Claude Code in a fresh terminal window or close and reopen the existing one. All 14 personas should now be available.

### Verify Restoration

**Claude Code Agent Files:**
```bash
ls -la ~/.claude/agents/
```

You should see 14 files:
```
art.md  bank.md  boss.md  boy.md  fah.md  joy.md  keng.md  khun-abe.md
nine.md  note.md  oat.md  poo.md  safe.md  toey.md
```

Try invoking a persona directly in Claude Code:
```
@art refactor this button component
@boy implement the login API endpoint
@toey run lint and typecheck
```

If the persona name autocompletes and responds with its persona-specific instructions (e.g., "Art | style, accessibility, responsive/dark-mode..."), the Claude Code restore was successful.

**Codex CLI Persona Config:**
```bash
ls -la ~/.codex/AGENTS.md ~/.agents/agents/AGENTS.md
```

Both files should exist and be identical:
```bash
diff ~/.codex/AGENTS.md ~/.agents/agents/AGENTS.md
```

If `diff` returns no output, they are synced correctly.

**opencode Persona Config:**
```bash
ls -la ~/.config/opencode/AGENTS.md
ls ~/.config/opencode/agents/ | wc -l
```

You should see `AGENTS.md` exist and the `agents/` folder should contain 15 files (13 core + 3 cavecrew):
```
art.md  bank.md  boy.md  cavecrew-builder.md  cavecrew-investigator.md
cavecrew-reviewer.md  fah.md  joy.md  keng.md  nine.md  note.md  oat.md
poo.md  safe.md  toey.md
```

If all files are present, the opencode restore was successful.

## Important: Dependent Skills

Many persona files reference specific skills in their `## Skills` sections. After restoring agents, **check that those referenced skills are also installed**:

- **Art** references: `tailwind-css-v4-shadcn-ui`, `frontend-design`, etc.
- **Boy** references: `go-fiber-v3`, etc.
- **Keng** references: `drizzle-orm`, `prisma`, etc.
- **Oat** references: `docker`, `github-actions-cicd`, etc.
- **Note** references: various documentation skills

If a skill is missing from `~/.claude/skills/`, the persona will load without that skill's context. To restore all skills as well:

1. If you have a backup of `~/.claude/skills/` from your previous machine, copy it:
   ```bash
   cp -r /path/to/backup/skills/* ~/.claude/skills/
   ```
2. Otherwise, reinstall missing skills manually or accept that some personas will have reduced context until you re-add them.

This skill intentionally does **not** attempt to auto-backup your entire `~/.claude/skills/` directory — that would be out of scope and require a separate backup mechanism.

## Keeping This Backup Current

### Claude Code Agents

When you edit a persona file in `~/.claude/agents/` (e.g., to add a new skill reference, refine a description, or update workflow rules), **re-copy that file into this skill folder** to keep the backup synchronized:

```bash
cp ~/.claude/agents/<name>.md <skill-path>/agents/<name>.md
```

Also update `PERSONAS_TABLE.md` if you:
- Add or remove a persona
- Change a persona's model tier
- Rename a persona

Then commit both the agent file and `PERSONAS_TABLE.md` to your `my-skills` git repository.

### Codex CLI Persona Config

When you edit `~/.codex/AGENTS.md` or `~/.agents/agents/AGENTS.md`, **re-copy the edited version into this skill's backup**:

```bash
# If you edited ~/.codex/AGENTS.md:
cp ~/.codex/AGENTS.md <skill-path>/codex/AGENTS.md

# If you edited ~/.agents/agents/AGENTS.md:
cp ~/.agents/agents/AGENTS.md <skill-path>/codex/AGENTS.md
```

**Important:** Keep both `~/.codex/AGENTS.md` and `~/.agents/agents/AGENTS.md` in sync by manually copying one to the other whenever you edit:

```bash
# After editing ~/.codex/AGENTS.md:
cp ~/.codex/AGENTS.md ~/.agents/agents/AGENTS.md

# Or after editing ~/.agents/agents/AGENTS.md:
cp ~/.agents/agents/AGENTS.md ~/.codex/AGENTS.md
```

Then commit the updated backup file to your `my-skills` git repository.

### opencode Persona Config

When you edit `~/.config/opencode/AGENTS.md` or any persona file in `~/.config/opencode/agents/`, **re-copy them into this skill's backup**:

```bash
# Copy the main AGENTS.md:
cp ~/.config/opencode/AGENTS.md <skill-path>/opencode/AGENTS.md

# Copy all agent files:
cp ~/.config/opencode/agents/*.md <skill-path>/opencode/agents/
```

Then commit the updated files to your `my-skills` git repository.

## Troubleshooting

### Claude Code: Personas not showing up after restore

1. Did you copy all 14 files to `~/.claude/agents/`? Run: `ls ~/.claude/agents/ | wc -l` — should be 14.
2. Did you update `~/.claude/CLAUDE.md`'s `## Personas` table? Check the table is there and properly formatted.
3. Did you start a **new** Claude Code session? Session scans happen at startup; a running session won't pick up new agents.

### Codex CLI: Config not loaded or out of sync

1. Did you restore both `~/.codex/AGENTS.md` and `~/.agents/agents/AGENTS.md`? Both must exist.
2. Are they identical? Run: `diff ~/.codex/AGENTS.md ~/.agents/agents/AGENTS.md` — should return no output.
3. If they differ, it indicates manual edits to only one file. Decide which is the source of truth, then copy it to the other location and re-sync this skill's backup.

### Some persona skills are unavailable

The persona .md files list skills they expect to find in `~/.claude/skills/`. If those skills are missing, the persona loads without them but still works. See the "Dependent Skills" section above for how to restore skills.

### opencode: Personas not loaded or out of sync

1. Did you restore both `~/.config/opencode/AGENTS.md` and all files in `~/.config/opencode/agents/`? Run: `ls ~/.config/opencode/agents/ | wc -l` — should be 15 (13 core + 3 cavecrew).
2. Did you restart the opencode editor? The editor scans configuration at startup; a running editor won't pick up newly restored files.
3. Are the YAML frontmatters in each `.md` file properly formatted (description, mode: subagent, color, permission)? Check a known-good file like `art.md` for reference.

### Persona file conflicts

If you've edited a persona locally and also restored from this backup, the restored version will overwrite. To merge manually:

1. Back up your edited version: `cp ~/.claude/agents/<name>.md ~/.claude/agents/<name>.md.local`
2. Restore from this skill: `cp <skill-path>/agents/<name>.md ~/.claude/agents/`
3. Open both files and manually merge the `## Skills` or `## Workflow` sections you customized.
4. Commit the merged version and re-copy it into the skill folder for the next restore.

## Summary

This skill is a **unified restore mechanism** for all three persona systems. Quick reference:

### Claude Code Restore
```bash
mkdir -p ~/.claude/agents && \
cp <skill-path>/agents/*.md ~/.claude/agents/
```

Then merge the personas table into `~/.claude/CLAUDE.md`, restart Claude Code, and you're back to full persona capacity.

### Codex CLI Restore
```bash
mkdir -p ~/.codex ~/.agents/agents && \
cp <skill-path>/codex/AGENTS.md ~/.codex/AGENTS.md && \
cp <skill-path>/codex/AGENTS.md ~/.agents/agents/AGENTS.md
```

### opencode Persona Config Restore
```bash
mkdir -p ~/.config/opencode/agents && \
cp <skill-path>/opencode/AGENTS.md ~/.config/opencode/AGENTS.md && \
cp <skill-path>/opencode/agents/*.md ~/.config/opencode/agents/
```

**Key points:**
- This backup is only as current as the last time you copied the persona files into it.
- **Keep Claude files current** by re-copying whenever you edit a persona in `~/.claude/agents/`, and commit changes to `my-skills` git repo.
- **Keep Codex file current** by re-copying whenever you edit `~/.codex/AGENTS.md` or `~/.agents/agents/AGENTS.md`, and commit to `my-skills` git repo.
- **Keep both Codex locations synced** — they must always be identical. If you edit one, copy it to the other manually.
- **Keep opencode files current** by re-copying whenever you edit `~/.config/opencode/AGENTS.md` or any persona in `~/.config/opencode/agents/`, and commit to `my-skills` git repo.
