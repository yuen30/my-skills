---
name: project-memory
description: Maintain lightweight per-project memory to avoid re-deriving facts across sessions. Write feedback notes and progress checkpoints; read them before non-trivial work to preserve context and apply learnings automatically.
---

# Project Memory: Cross-Session Context Retention

A behavioral skill for maintaining a lightweight, per-project memory so personas don't re-derive already-known facts, decisions, and corrections across sessions. This is **not a backup mechanism** — it's a practice of writing and reading context during development work.

## What Is This?

As you work on a project across multiple sessions, you and the user may:
- Discover project-specific patterns or conventions worth remembering (e.g., "always run migrations with the wrapper script, not raw sql")
- Hit architectural decisions that would be expensive to re-derive (e.g., "this repo uses the mock/real adapter pattern")
- Reach meaningful checkpoints on multi-session tasks (e.g., "we refactored 12 of 30 components; remaining 18 are...")
- Record explicit user corrections or preferences that should apply going forward

**Without memory:** Every session re-analyzes from scratch. Lessons learned are forgotten. The user repeats corrections. Multi-session work loses context and restarts.

**With memory:** A lightweight index points to relevant context. New sessions scan it before digging into code. User feedback is captured once and applied automatically. Multi-session tasks resume with a clear checkpoint.

---

## Where Memory Lives

Memory is stored **inside each project's own repository** at:

```
<project-root>/.agents/memory/MEMORY.md
<project-root>/.agents/memory/<topic>.md
```

### Examples

- Project: `eordering-vn` (repository at `/Users/taweechai/Documents/GitHub/eordering-vn`)
  - Memory directory: `/Users/taweechai/Documents/GitHub/eordering-vn/.agents/memory/`
  - Main index: `/Users/taweechai/Documents/GitHub/eordering-vn/.agents/memory/MEMORY.md`

- Project: `my-skills` (repository at `/Users/taweechai/Documents/GitHub/my-skills`)
  - Memory directory: `/Users/taweechai/Documents/GitHub/my-skills/.agents/memory/`
  - Main index: `/Users/taweechai/Documents/GitHub/my-skills/.agents/memory/MEMORY.md`

**Why per-project storage in the project's own repo:**
1. **Git-tracked with the project:** Memory lives alongside the code it documents. It travels with the project to any machine and is automatically backed up as part of that project's git history — no separate backup step needed.
2. **Scoped naturally to the project:** No project-name collisions, no dependency on a central `my-skills` checkout, and memory is always available to anyone who clones the project.
3. **Portable:** Collaborators automatically get the project's memory when they clone the repo; decisions and learnings don't stay locked in a central store.

Memory files are committed to **that project's own git repository**, not to `my-skills`. This ensures memory stays bound to the project throughout its lifecycle.

---

## File Structure

### MEMORY.md — Index of Topics

A short markdown file listing all known topics as bullets, each with a markdown link and one-line description:

```markdown
- [Use make test, not go test directly](feedback_test_runner.md) — always invoke make test in this repo, ensures correct flags
- [Auth migration progress](auth_migration_progress.md) — 3 of 8 endpoints done; remaining 5 still on session cookies
- [Prefer composition over inheritance](feedback_composition.md) — keep classes small, favor small composed units
- [Repository pattern architecture](repository_pattern_config.md) — all data access through repo/ interfaces, never direct ORM
- [Deploy checklist](feedback_deploy_checklist.md) — run smoke tests before promoting to prod
```

**Principles:**
- **Index only, not exhaustive.** MEMORY.md is a "table of contents," not a history dump.
- **One line per topic.** If a bullet is longer than a line, move details to the linked file.
- **Keep it short.** Scan-friendly; typical MEMORY.md is 5–15 bullets.

### Topic Files — One Per Subject

Each link points to a small standalone markdown file with the full details. Filenames follow a convention:

- **feedback_<topic>.md** — User feedback, preferences, or corrections that should apply going forward.
  - Examples: `feedback_use_bun.md`, `feedback_terse_responses.md`, `feedback_issue_labels.md`
  - Content: What the user said, why it matters, what to do next time.

- **<task>_progress.md** — Checkpoint for a multi-session task that's in progress or recently completed.
  - Examples: `refactor_progress.md`, `api_migration_progress.md`, `testing_setup_progress.md`
  - Content: What's done, what's remaining, key findings, blockers.

- **<topic>_config.md** — Architectural or configuration decision that's expensive to re-derive.
  - Examples: `global_agent_config.md`, `adapter_pattern_config.md`, `auth_setup_config.md`
  - Content: What the decision was, why, where it's implemented, which files are affected.

---

## When to WRITE a Memory Note

### Trigger 1: User Gives Explicit Feedback or Correction

When the user corrects you or states a preference that should apply to all future work in this project, write a `feedback_<topic>.md` file and add it to MEMORY.md.

**Example:** User says, "Always use `make test` to run tests in this repo, not direct test commands."

```markdown
# feedback_test_runner.md

## What the User Said

Always use the `make test` command to run tests in this repository, not `go test` directly. This ensures tests run with the correct build flags and environment setup.

## Why

- Consistency: the Makefile is configured with proper flags and environment setup for this project.
- Build flags: tests must run with `-tags=integration` to pick up integration test files.
- Dependency versions: the Makefile locks test dependencies; running tests directly can pick up system versions.

## Action

On all future work in this project, when running tests:
- Use `make test` instead of `go test`
- Use `make test-unit` for unit tests only
- Use `make test-integration` for integration tests only
- Never run `go test ./...` directly

## Set By

User feedback, session 2024-05-15
```

Then add to MEMORY.md:
```markdown
- [Use make test, not go test directly](feedback_test_runner.md) — always invoke make test in this repo, ensures correct flags
```

### Trigger 2: Multi-Session Task Reaches a Milestone

When a task that will take multiple sessions reaches a meaningful checkpoint, write a `<task>_progress.md` file to help the next session resume without re-deriving what's already done.

**Example:** You've been migrating authentication across multiple sessions. By session 2, you've migrated three endpoints and the next session should know the status.

```markdown
# auth_migration_progress.md

## Task

Migrate authentication from session cookies to JWT tokens across all API endpoints.

## Why

- Current: session-based auth requires server-side state, doesn't scale across services
- Goal: JWT tokens enable stateless auth, easier horizontal scaling, per-endpoint expiration control

## Done (Sessions 1–2)

3 of 8 endpoints migrated:
- `/api/auth/login` → returns JWT in response body, sets httpOnly cookie fallback
- `/api/auth/refresh` → exchanges refresh token for new JWT
- `/api/users/profile` → accepts JWT in Authorization header

All tests passing. No regressions observed.

## Remaining

5 endpoints still using session cookies:
- `/api/orders/` (3 endpoints: list, create, update)
- `/api/customers/` (2 endpoints: list, details)

## Key Findings

1. **Middleware order:** Always verify JWT middleware runs before business logic middleware.
2. **Cookie fallback:** Keep httpOnly cookie for older clients while JWT is being rolled out.
3. **Token claims:** Include user ID and role in JWT; don't rely on session state for authorization checks.

## Blockers

None. Ready to continue in next session.

## Set By

Session 2024-02-01, after login and refresh endpoints complete
```

Then add to MEMORY.md:
```markdown
- [Webapp clean-code refactor progress](refactor_progress.md) — 12 of 30 components done; remaining 18 in old style
```

### Trigger 3: Architectural or Config Decision Is Made

When the team or user decides on a pattern or config that would be expensive to re-discover (e.g., "we use the adapter pattern for mock/real switching," "CI only runs on main and dev"), write a `<topic>_config.md` file.

**Example:** The project uses a repository-pattern abstraction over database access, and you want to record this architectural decision so all future data work follows the same pattern.

```markdown
# repository_pattern_config.md

## Decision

This project uses a repository-pattern abstraction over the database layer. All data access goes through `internal/repo/` interfaces, never direct ORM calls.

## Pattern

- **Repository interface** in `internal/repo/interfaces.go` defines Read/Write/Delete contracts
- **Concrete implementation** in `internal/repo/postgres.go` (GORM)
- **In-memory mock** in `internal/repo/mock.go` for unit tests

All service code calls repo methods, never raw SQL or ORM queries.

## Config Location

- Interface definitions: `internal/repo/interfaces.go`
- PostgreSQL implementation: `internal/repo/postgres.go`
- Mock implementation: `internal/repo/mock.go`
- Wiring: `cmd/server/main.go` (injected into service constructors)

## When to Edit

If you need to:
- Add a new query type, add a method to the interface in `interfaces.go`, implement it in postgres.go and mock.go
- Change ORM behavior, edit only `internal/repo/postgres.go`
- Add a mock-specific behavior, edit only `internal/repo/mock.go`

Do NOT:
- Call ORM directly from service code
- Bypass the repo interface
- Add data access logic in handlers or controllers

## Set By

Architecture decision, established in project setup
```

Then add to MEMORY.md:
```markdown
- [Repository pattern architecture](repository_pattern_config.md) — all data access through repo/ interfaces, never direct ORM
```

---

## When to READ Memory

### Trigger: Starting a Non-Trivial Task

Before diving into code analysis, architectural decisions, or multi-file refactoring in any project, **scan MEMORY.md for relevant context**. Create the `.agents/memory/` folder if it doesn't exist yet (first session for that project).

**Example workflow:**

1. **User asks:** "Add a new field to the checkout flow."
2. **You respond:** "Let me check the project memory first..."
3. **You read:** `<project-root>/.agents/memory/MEMORY.md`
4. **You see:** "Use make test, not go test directly" and "Repository pattern architecture" and "Auth migration in progress"
5. **You now know:**
   - Run tests via `make test`
   - Add data access through the repository layer, not raw ORM calls
   - Auth migration is mid-flight; check its progress note before touching auth code
6. **You don't re-derive:** How to run tests, how data access is structured, whether auth is stable or mid-migration

---

## File Format Convention

Each memory note file is a simple markdown document. Use headings, bullets, and code blocks freely:

```markdown
# topic_title

## Context

Why does this matter? What was the problem?

## Decision / Solution

What was decided or what did you learn?

## Implementation / Action Items

What should you do next time you encounter this?

- Bullet item
- Bullet item

## Example

```code block```

## Set By

Who created this? When? Which session or PR?
```

**Keep notes terse:** A note should be skimmable in 30 seconds. If it's getting long, split it into two notes.

---

## Updating Existing Memory

As you work, you may find that a memory note is outdated:

1. **Edit the .md file directly** with new information (e.g., "15 of 30 components done now").
2. **Update the MEMORY.md line** if the one-liner description changed.
3. **Do not delete** notes unless the topic is genuinely obsolete (e.g., a temporary blocker that's now resolved).
4. **Commit memory changes to that project's git repo** — since memory lives inside the project, it's committed like any other project change using that project's own commit conventions.

**Example update:** The refactor progress note showed 12 of 30 done. After session 3, update it to 18 of 30:

```markdown
# refactor_progress.md (UPDATED after session 3)

## Done (Sessions 1–3)

18 of 30 components refactored:
- ... (original 12 plus 6 new ones)

## Remaining

12 components still in old style:
- `src/components/products/` (8 files)
- `src/components/dashboard/` (4 files)

## Set By

Session 2024-01-22 → Session 2024-01-29 (incremental updates)
```

And update MEMORY.md:
```markdown
- [Webapp clean-code refactor progress](refactor_progress.md) — 18 of 30 components done; remaining 12 in old style
```

Then commit both changes to **that project's git repository** (e.g., `yuen30/eordering-vn`, not `my-skills`).

---

## Cross-Project Behavior

This skill applies to **any project** where you have a working directory. The memory system is:

- **Per-project:** Each project has its own `.agents/memory/` folder inside the project's own git repository.
- **Persistent:** Memory survives sessions. New sessions read MEMORY.md at task start.
- **Lightweight:** No overhead; just markdown files in a directory.
- **Portable and backed up:** Memory lives in each project's own git repo, so it's automatically backed up and synced across machines as part of that project's history without a separate backup step.

---

## Checklist: Did You Create Memory?

After work on a project, ask:

- [ ] Did the user correct me or state a preference that should apply next time? → Write `feedback_<topic>.md`
- [ ] Did I hit a multi-session task milestone? → Write or update `<task>_progress.md`
- [ ] Did I discover an expensive-to-re-derive architectural decision? → Write `<topic>_config.md`
- [ ] Have I added to or updated MEMORY.md to link new notes? → Check the index is up to date

---

## Distinction: Memory vs. Backup

**This skill is NOT a backup mechanism.**

A backup mechanism (like the `my-agent` skill) copies entire directories to preserve them across machine resets — a one-time rescue tool.

**This skill is the PRACTICE of maintaining memory during development.** It's:
- Ongoing (not one-time)
- Lightweight (not heavy backup dumps)
- Focused on context and corrections (not archives)
- Collaborative (user feedback is remembered and applied)

If you ever need to back up your entire `~/.claude/` for a machine reset, that's a separate concern (would use a dedicated backup mechanism). This skill is about work in progress and learnings from the current project lifecycle.

---

## Quick Start

1. **Check if memory exists:** `ls <project-root>/.agents/memory/` — if empty or missing, you're starting fresh for that project.

2. **Create MEMORY.md:** Start with a few bullets if you know the topics, or leave it empty until the first feedback/decision.

3. **As you work:** When user feedback comes in or a decision is made, create the corresponding topic file (feedback_*.md or *_progress.md) and link it in MEMORY.md.

4. **Next session:** Scan MEMORY.md before diving into code. Check any relevant topic files.

5. **Update as you go:** Refresh progress notes, add new feedback, keep the index current. Commit memory changes to **that project's git repository** using that project's standard commit conventions.

---

## See Also

- `my-agent` — Backup/restore mechanism for your subagent system (different from this skill; this skill is for project-level memory, not persona recovery).

This is the ongoing practice of maintaining project memory during active development, distinct from one-time backup/restore tools.
