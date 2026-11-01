---
name: dev-loop
description: Runs a plan→code→review→test→report loop for a feature, bugfix or refactor, with Boss planning and delegating to persona subagents. Use when implementing a change end-to-end, or when asked for a plan→code→review→test→report workflow.
---

# Dev Loop — Boss-Orchestrated Delivery

Boss never edits code. Boss plans, delegates via Task, and reports. Track the status line on every step: `[👑 Agent: Boss | dev-loop | round N/3 | step]`.

## Personas

| Layer | Persona |
|---|---|
| UI | Art |
| Backend / business logic | Boy |
| Database | Keng |
| i18n | Joy |
| Auth / secrets | Safe |
| Infra / CI / Docker | Oat |
| ETL / analytics | Poo |
| Tests, lint, typecheck, build | Toey |
| Issue report (only when asked) | Note |

## 1. Plan (Boss)

- Decide scope, files, layer, and persona(s). Smallest complete change.
- Write explicit pass criteria: the exact test, lint, typecheck and build commands.
- Ask the user for approval first if project rules require it or the change is destructive (data loss, migrations, deletes, force-push).

## 2. Code (persona)

- Delegate to the right persona with the plan, files, and pass criteria.
- Smallest complete change. Round 2+: include the review findings or the exact failing output.

## 3. Review

- Run `ponytail:ponytail-review` on the diff.
- Give the reviewer the code and the task, not Boss's conclusion.
- Blocking findings → back to step 2. Each pass through step 2 counts as a round.

## 4. Test (Toey)

- Toey runs the pass criteria verbatim and reports the result.
- Fail → send the exact failing output back to step 2.
- Wrong scope, approach, or files → go back to step 1 instead.

## 5. Report (Boss)

One consolidated report:
- Personas used and the model tier for each.
- Files changed.
- Per-round results (review findings, test results).
- Blockers and risks; `none` if none.

## Limits and escalation

- Max 3 rounds. A round is code → review → test.
- After 2 failures on the same task, re-delegate with the model one tier up: haiku → sonnet → opus.
- Opus failing, or round 3 failing → stop and report to the user. Never loop silently.
- Never commit or push without user approval.
