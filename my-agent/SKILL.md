---
name: my-agent
description: Backs up and restores Claude Code personas (~/.claude/agents), plus Codex CLI and opencode persona configs. Use when restoring or syncing personas after a machine reset, or when parking or unparking a persona.
---

# my-agent: Persona Backup and Restore

`<repo>` below means the root of this `my-skills` clone.

## What it backs up

| Platform | Repo path | Live location | Restored by |
|---|---|---|---|
| Claude Code, 10 active personas | `my-agent/agents/*.md` | `~/.claude/agents/` | `install.sh` |
| Claude Code, 4 parked personas | `my-agent/agents-disabled/*.md` | `~/.claude/agents-disabled/` | `install.sh` |
| Codex CLI (one unified file) | `my-agent/codex/AGENTS.md` | `~/.codex/AGENTS.md` and `~/.agents/agents/AGENTS.md` (keep identical) | manual |
| opencode | `my-agent/opencode/AGENTS.md`, `my-agent/opencode/agents/*.md` | `~/.config/opencode/` | manual |

- Active (10): boss, art, boy, toey, oat, keng, joy, safe, poo, note.
- Parked (4): nine, fah, bank, khun-abe. Never activated by `install.sh`.
- opencode mirror has 12 core personas plus 3 cavecrew helpers (`cavecrew-builder`, `-investigator`, `-reviewer`). It is a reference, not a copy of the Claude set.
- `PERSONAS_TABLE.md`: roster of 10 active + 4 parked personas; frontmatter in `agents/` and `agents-disabled/` is authoritative for model tiers.

## Persona roster

| Persona | Scope | Model |
|---|---|---|
| Boss 👑 | Architecture, scope, delegation, change-risk review | opus |
| Art 🎨 | UI/UX, accessibility, Tailwind, shadcn/ui | sonnet |
| Boy ⚙️ | Backend, business logic, integrations | sonnet |
| Toey 🧪 | Tests, lint, typecheck, build | haiku |
| Oat 🐳 | Docker, CI/CD, deployment, observability | sonnet |
| Keng 💾 | Database, ORM, safe migrations | opus |
| Joy 🌐 | i18n, locale routing, translations | haiku |
| Safe 🛡️ | Auth, authorization, secrets, OWASP | opus |
| Poo 📊 | ETL, analytics, reports, performance | sonnet |
| Note 📄 | API docs, runbooks, Thai issue summaries | haiku |

Each persona file has frontmatter (name, description, tools, model) and a `## Skills` section naming the skills it loads from `~/.claude/skills/`.

## Restore

### Claude Code (skills and personas)

```bash
cd <repo> && ./install.sh
```

- Skills: each `<repo>/*/SKILL.md` folder replaces `~/.claude/skills/<name>/`; stale entries are pruned via the manifest `~/.claude/skills/.my-skills-installed`.
- Personas: `my-agent/agents/*.md` goes to `~/.claude/agents/`; `my-agent/agents-disabled/*.md` goes to `~/.claude/agents-disabled/`.
- Safe to re-run. Start a new Claude Code session afterwards; agents are scanned at startup.

Verify:

```bash
ls ~/.claude/agents          # 10 files
ls ~/.claude/agents-disabled # 4 files
```

### Codex CLI (manual)

```bash
mkdir -p ~/.codex ~/.agents/agents
cp <repo>/my-agent/codex/AGENTS.md ~/.codex/AGENTS.md
cp <repo>/my-agent/codex/AGENTS.md ~/.agents/agents/AGENTS.md
diff ~/.codex/AGENTS.md ~/.agents/agents/AGENTS.md   # no output = in sync
```

### opencode (manual)

```bash
mkdir -p ~/.config/opencode/agents
cp <repo>/my-agent/opencode/AGENTS.md ~/.config/opencode/AGENTS.md
cp <repo>/my-agent/opencode/agents/*.md ~/.config/opencode/agents/
ls ~/.config/opencode/agents | wc -l   # 15
```

Restart opencode afterwards.

## Park and unpark a persona

Parked personas live in `~/.claude/agents-disabled/` so Claude Code does not load them.

```bash
mv ~/.claude/agents/<name>.md ~/.claude/agents-disabled/      # park
mv ~/.claude/agents-disabled/<name>.md ~/.claude/agents/      # unpark
```

Start a new session afterwards. To make it permanent in the backup, move the file between `my-agent/agents/` and `my-agent/agents-disabled/` in the repo and update the `## Personas` table in `~/.claude/CLAUDE.md`.

## Per-persona skills

Skills are installed by `install.sh`. A missing skill only means that persona loads without its context. Names with a plugin prefix come from plugins, not this repo.

- **Boss**: `find-skills`, `project-structure`, `abe-framework`, `abe-ui`, `ci-cd`, `monorepo-scaffold-nextjs-go`, `context7-auto-research`, `web-research`, `project-memory`, `ship`, `my-agent`, `ponytail:ponytail-review`, `ponytail:ponytail-audit`. Names stack skills in delegation briefs instead of loading them.
- **Art**: `abe-ui`, `abe-framework`, `frontend-design:frontend-design`, `context7-auto-research`, `project-structure`, `web-research`, `project-memory`.
- **Boy**: `abe-framework`, `abe-data`, `vercel:ai-sdk`, `http-status-codes`, `context7-auto-research`, `project-structure`, `web-research`, `project-memory`.
- **Toey**: `abe-framework`, `ponytail:ponytail-review`, `ponytail:ponytail-audit`, `project-memory`.
- **Oat**: `docker`, `ci-cd`, `redis`, `rabbitmq`, `web-research`, `project-memory`.
- **Keng**: `abe-data`, `abe-framework`, `project-memory`.
- **Joy**: `project-memory`.
- **Safe**: `abe-framework`, `ponytail:ponytail-review`, `project-memory`.
- **Poo**: `web-research`, `project-memory`.
- **Note**: `project-structure`, `postman:api-documentation`, `http-status-codes`, `monorepo-scaffold-nextjs-go`, `web-research`, `project-memory`, `my-agent`, `ship`.

## Keeping the backup current

After editing a live persona or config, copy it back into the repo and commit:

```bash
cp ~/.claude/agents/<name>.md <repo>/my-agent/agents/<name>.md
cp ~/.codex/AGENTS.md <repo>/my-agent/codex/AGENTS.md              # then sync ~/.agents/agents/AGENTS.md
cp ~/.config/opencode/AGENTS.md <repo>/my-agent/opencode/AGENTS.md
cp ~/.config/opencode/agents/*.md <repo>/my-agent/opencode/agents/
```

Parked personas: copy from `~/.claude/agents-disabled/` into `my-agent/agents-disabled/`.

## Troubleshooting

- Personas missing in Claude Code: run `./install.sh`, check `ls ~/.claude/agents | wc -l` is 10, and start a new session.
- Parked persona not reinstalled to `~/.claude/agents/`: expected; `install.sh` skips any persona already present in `~/.claude/agents-disabled/`.
- Local persona edits overwritten by a restore: save `<name>.md.local` first, restore, merge by hand, then copy the result back into the repo.
- Codex out of sync: `diff ~/.codex/AGENTS.md ~/.agents/agents/AGENTS.md`; pick the source of truth, copy it to the other, and re-copy into the repo.
