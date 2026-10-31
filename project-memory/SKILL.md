---
name: project-memory
description: Records what is being worked on and how far it has got, stored inside each project, so the next session resumes without re-deriving. Use when starting, pausing, or finishing multi-step work in a project, or when asked where work stands.
---

# Project Memory — Work Progress per Project

Keep a short, current note of **what is being worked on and how far it has got**, inside the project itself. Not a backup, not a preference store.

## Location

```
<project-root>/.agents/memory/MEMORY.md          # index: one line per task
<project-root>/.agents/memory/<task>_progress.md # one file per task
```

Create the folder on first use. Commit it with the project's own repo, never to my-skills.

## Read — at the start of non-trivial work

1. Read `MEMORY.md`; open only the progress file(s) relevant to the request.
2. Check it is still true: compare with `git log --oneline -10` and `git status --short`. If the code moved on, trust git and fix the note.
3. Tell the user in one line what you are resuming from. Do not redo steps marked done.

## Write — when any of these happens

- A step or milestone of the task is finished.
- Work pauses or the session is about to end with work unfinished.
- A blocker or a decision that changes the plan appears.

## Progress file template

```markdown
# <Task name>
Status: in-progress | blocked | done — updated <YYYY-MM-DD>

## Goal
<one or two lines>

## Done
- <step> (<commit sha or file>)

## Now
- <what is in flight right now>

## Next
- <next concrete step>

## Blockers / Decisions
- <only if any>
```

Index line in `MEMORY.md`:

```markdown
- [<Task name>](<task>_progress.md) — <status>: <one-line where it stands>
```

## Rules

- Keep each progress file under ~40 lines. Rewrite stale lines; do not append history.
- Record facts that are expensive to re-discover (what is done, where, what is next). Do not paste code, diffs, or logs.
- When a task is done: set `Status: done`, keep a one-line summary in the index, delete the details once no longer useful.
- One task per file; name it `<task>_progress.md` in snake_case.
