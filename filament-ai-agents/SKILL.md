---
name: filament-ai-agents
description: Use when an AI agent must create, inspect, implement, debug, upgrade, or review a Laravel application that uses Filament PHP. Resolves version-matched Markdown documentation from the installed packages under vendor/filament before code changes and avoids guessing APIs from training data.
---

# Filament AI Agents

Treat the documentation bundled with the project's installed Filament packages as the source of truth. Filament APIs and conventions can differ across versions, so do not rely on memory when local version-matched documentation is available.

## Required workflow

1. Start from the Laravel application or file being changed and find the nearest `composer.json` and `composer.lock`.
2. Inspect the locked `filament/*` package versions. Resolve Composer's actual vendor directory instead of assuming the repository root or a fixed `vendor/` path.
3. Confirm which Filament packages are installed by inspecting Composer metadata and directories under `<vendor-dir>/filament/`.
4. List the available Markdown documentation, then search filenames, headings, and content for the requested feature.
5. Read the smallest relevant package/topic documents before writing code. Follow linked prerequisite or migration documents when they affect the task.
6. Inspect existing application conventions, resources, pages, relation managers, schemas, policies, and tests before choosing an implementation.
7. Implement outside `vendor/`. Never edit generated dependency files or copy Filament's bundled documentation into the application or this skill.
8. Run the project's narrowest relevant checks, followed by any required formatter, static analysis, tests, or build commands defined by the repository.

## Documentation discovery

Use repository-aware commands and quote resolved paths:

```bash
composer show --locked 'filament/*'
composer config vendor-dir --absolute
rg --files "<vendor-dir>/filament" -g '*.md' | rg '/docs/'
rg -n -i "<feature|component|method>" "<vendor-dir>/filament" -g '*.md'
```

Common documentation owners include:

- `actions/docs/` for actions, modals, imports, exports, and lifecycle behavior
- `forms/docs/` for fields, validation, uploads, repeaters, and form behavior
- `infolists/docs/` for read-only entries and custom entries
- `notifications/docs/` for session, database, and broadcast notifications
- `schemas/docs/` for layouts, sections, tabs, wizards, and custom components
- `tables/docs/` for columns, filters, actions, summaries, grouping, and table behavior
- `widgets/docs/` for overview, stats, and chart widgets

Package layout is version-dependent. Discover what is actually installed instead of treating this list as exhaustive.

## Selecting evidence

- Prefer bundled docs from the exact locked package version.
- Read source code in the installed package when bundled docs do not define the behavior precisely.
- Use official Filament documentation matching the installed major and minor version only when local docs are missing or incomplete.
- Treat blog posts, snippets, and answers for another Filament version as unverified until confirmed against local docs or source.
- Heed deprecation, upgrade, and breaking-change notices before reusing an older project pattern.
- Record the package version and documents consulted when version-sensitive behavior materially affects the result.

## Missing dependencies or docs

If `composer.lock`, installed packages, or bundled docs are unavailable:

1. Inspect the repository's Composer setup and installation instructions.
2. State what is missing and request or run `composer install` only when dependency installation is within scope and authorized.
3. Do not invent Filament classes, namespaces, methods, configuration keys, or filesystem structure.
4. If installation is not possible, use official version-matched docs as a clearly reported fallback and mark remaining assumptions.

## Completion criteria

- The implementation matches the locked Filament version and installed packages.
- Relevant bundled documentation was read before version-sensitive code was written.
- Existing Laravel and Filament project conventions remain intact.
- No file under the Composer vendor directory was modified or committed.
- Repository-defined verification passed, or each failure and unverified assumption was reported explicitly.
