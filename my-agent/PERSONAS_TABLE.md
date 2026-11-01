# Personas Table Reference

10 active personas (`my-agent/agents/`) and 4 parked ones (`my-agent/agents-disabled/`, installed to `~/.claude/agents-disabled/`, never auto-activated). Model tiers come from each file's frontmatter. Keep in sync with `~/.claude/CLAUDE.md`.

| Persona | Emoji | Scope |
|---|---|---|
| Boss | 👑 | Architecture, scope, stability, coordination |
| Art | 🎨 | UI/UX, accessibility, Tailwind, shadcn/ui |
| Boy | ⚙️ | Backend, business logic, integrations |
| Toey | 🧪 | Tests, lint, typecheck, build |
| Oat | 🐳 | Docker, CI/CD, deployment, observability |
| Keng | 💾 | Database, ORM, safe migrations |
| Joy | 🌐 | i18n, locale routing, translations |
| Safe | 🛡️ | Auth, authorization, secrets, OWASP |
| Poo | 📊 | ETL, analytics, reports, performance |
| Note | 📄 | API docs, runbooks, handover notes |
| Nine | 📱 | Mobile app development (iOS/Android, React Native) (parked) |
| Fah | 🚨 | Production reliability, incident response, on-call (parked) |
| Bank | 🤖 | Data engineering, ML pipelines (parked) |
| khun-abe | (catch-all) | Global orchestrator / fallback agent (parked) |

## Model Tiers

| Persona | Model | Effort |
|---|---|---|
| Boss | opus | medium |
| Art | sonnet | medium |
| Boy | sonnet | medium |
| Toey | haiku | low |
| Oat | sonnet | medium |
| Keng | opus | high |
| Joy | haiku | low |
| Safe | opus | high |
| Poo | sonnet | medium |
| Note | haiku | low |
| Nine | sonnet | — |
| Fah | opus | — |
| Bank | opus | — |
| khun-abe | inherit | — |
