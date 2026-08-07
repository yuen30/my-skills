---
name: my-agent
description: Backup and restore the complete 13-persona Claude Code subagent system. Restores all persona definitions (Boss, Art, Boy, Toey, Oat, Keng, Joy, Safe, Poo, Note, Nine, Fah, Bank) plus the khun-abe catch-all orchestrator to ~/.claude/agents/ after a machine reset.
---

# my-agent: Personal Persona Backup & Restore

Backup and restore mechanism for your complete 13-persona Claude Code subagent system, plus the khun-abe global orchestrator. On a fresh machine, this skill lets you instantly restore all persona definitions without manual recreation.

## What Is This?

This is a **living backup** of your multi-agent development system:

- **13 specialist personas**: Each handles a distinct domain (UI, backend, testing, database, i18n, auth, analytics, documentation, mobile, production reliability, ML pipelines).
- **1 global catch-all**: `khun-abe` is the entry point for unspecialized or cross-cutting work.
- **Per-persona configuration**: Each persona is defined as a `~/.claude/agents/<name>.md` file with:
  - **Frontmatter**: name, description, tools list, model tier (opus/sonnet/haiku)
  - **Skills section**: list of loaded skills (from `~/.claude/skills/`)
  - **Workflow section**: persona-specific operating rules
  - **Global rules section**: inherited from `~/.claude/CLAUDE.md`

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

### Prerequisites

- Claude Code is installed and initialized (at least one session completed to create `~/.claude/` directory)
- You have this skill in your skills library: `/Users/taweechai/Documents/GitHub/my-skills/my-agent/`

### Step 1: Copy Agent Files

```bash
mkdir -p ~/.claude/agents
cp /Users/taweechai/Documents/GitHub/my-skills/my-agent/agents/*.md ~/.claude/agents/
```

This restores all 14 persona `.md` files to their canonical location.

### Step 2: Merge the Personas Table into ~/.claude/CLAUDE.md

Your fresh `~/.claude/CLAUDE.md` will already have a basic `## Personas` table (with default entries). Replace it with the one from this skill:

1. Open `/Users/taweechai/Documents/GitHub/my-skills/my-agent/PERSONAS_TABLE.md` — copy the full table (both roster and model tiers sections).
2. Open `~/.claude/CLAUDE.md` — find the existing `## Personas` section and replace the entire table with the copied content.
3. Save.

Alternatively, if you want to preserve any other custom content in `~/.claude/CLAUDE.md`, just ensure the `## Personas` table matches the one in `PERSONAS_TABLE.md`.

### Step 3: Start a New Claude Code Session

Agent configurations are scanned at session start. After restoring the persona files and updating `CLAUDE.md`, open Claude Code in a fresh terminal window or close and reopen the existing one. All 14 personas should now be available.

### Verify Restoration

List the restored agents:
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

If the persona name autocompletes and responds with its persona-specific instructions (e.g., "Art | style, accessibility, responsive/dark-mode..."), the restore was successful.

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

When you edit a persona file in `~/.claude/agents/` (e.g., to add a new skill reference, refine a description, or update workflow rules), **re-copy that file into this skill folder** to keep the backup synchronized:

```bash
cp ~/.claude/agents/<name>.md /Users/taweechai/Documents/GitHub/my-skills/my-agent/agents/<name>.md
```

Also update `PERSONAS_TABLE.md` if you:
- Add or remove a persona
- Change a persona's model tier
- Rename a persona

Then commit both the agent file and `PERSONAS_TABLE.md` to your `my-skills` git repository.

## Troubleshooting

### Personas not showing up after restore

1. Did you copy all 14 files to `~/.claude/agents/`? Run: `ls ~/.claude/agents/ | wc -l` — should be 14.
2. Did you update `~/.claude/CLAUDE.md`'s `## Personas` table? Check the table is there and properly formatted.
3. Did you start a **new** Claude Code session? Session scans happen at startup; a running session won't pick up new agents.

### Some persona skills are unavailable

The persona .md files list skills they expect to find in `~/.claude/skills/`. If those skills are missing, the persona loads without them but still works. See the "Dependent Skills" section above for how to restore skills.

### Persona file conflicts

If you've edited a persona locally and also restored from this backup, the restored version will overwrite. To merge manually:

1. Back up your edited version: `cp ~/.claude/agents/<name>.md ~/.claude/agents/<name>.md.local`
2. Restore from this skill: `cp /Users/taweechai/Documents/GitHub/my-skills/my-agent/agents/<name>.md ~/.claude/agents/`
3. Open both files and manually merge the `## Skills` or `## Workflow` sections you customized.
4. Commit the merged version and re-copy it into the skill folder for the next restore.

## Summary

This skill is a **one-command restore** for your entire personal agent system:

```bash
mkdir -p ~/.claude/agents && \
cp /Users/taweechai/Documents/GitHub/my-skills/my-agent/agents/*.md ~/.claude/agents/
```

After that, merge the `## Personas` table into `~/.claude/CLAUDE.md` (or just copy the whole CLAUDE.md if you don't have other customizations), restart Claude Code, and you're back to full persona capacity.

**Key point:** This backup is as good as the last time you copied the persona files into it. Keep it current by re-copying whenever you edit a persona locally, and commit those changes to your `my-skills` git repo.
