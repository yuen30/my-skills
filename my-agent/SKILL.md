---
name: my-agent
description: Backs up and restores Claude Code personas (~/.claude/agents), plus Codex CLI and opencode persona configs. Use when restoring or syncing personas after a machine reset, or when parking or unparking a persona.
---

# my-agent: Persona Backup and Restore

`<repo>` below means the root of this `my-skills` clone.

Backs up Claude Code personas (10 active in `my-agent/agents/`, 4 parked in `my-agent/agents-disabled/`), plus Codex CLI and opencode configs. Claude Code restore: `cd <repo> && ./install.sh`, then start a new session.

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

## Park and unpark a persona

Parked personas live in `~/.claude/agents-disabled/` so Claude Code does not load them.

```bash
mv ~/.claude/agents/<name>.md ~/.claude/agents-disabled/      # park
mv ~/.claude/agents-disabled/<name>.md ~/.claude/agents/      # unpark
```

Start a new session afterwards. To make it permanent in the backup, move the file between `my-agent/agents/` and `my-agent/agents-disabled/` in the repo and update the `## Personas` table in `~/.claude/CLAUDE.md`.

## Per-persona skills

Skills are installed by `install.sh`. A missing skill only means that persona loads without its context. Names with a plugin prefix come from plugins, not this repo.

After install, run `python3 my-agent/scripts/check_installed.py` to confirm every skill named by the installed personas is available (exit 1 lists the missing ones).

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

Full restore for Codex CLI and opencode, what each path maps to, backup maintenance, and troubleshooting: [references/restore.md](references/restore.md)
