# Personas Table Reference

This table is the authoritative roster of all 13 personas in the Khun Abe agent system, plus the khun-abe catch-all. Keep this in sync with `~/.claude/CLAUDE.md` when adding/removing personas.

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
| Nine | 📱 | Mobile app development (iOS/Android, React Native) |
| Fah | 🚨 | Production reliability, incident response, on-call |
| Bank | 🤖 | Data engineering, ML pipelines |
| khun-abe | (catch-all) | Global orchestrator / fallback agent |

## Model Tiers

| Persona | Model |
|---|---|
| Boss | opus |
| Art | sonnet |
| Boy | sonnet |
| Toey | haiku |
| Oat | sonnet |
| Keng | opus |
| Joy | haiku |
| Safe | opus |
| Poo | sonnet |
| Note | haiku |
| Nine | sonnet |
| Fah | sonnet |
| Bank | opus |
| khun-abe | inherit |
