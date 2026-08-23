# skill_version_audit_progress.md

## Task

Full-repository audit of all Claude Code skill packs in my-skills for version-staleness (hardcoded version numbers presented as "current" without a dynamic detect-installed-version step).

## Why

Skills that hardcode version numbers (e.g., "Django 5.0 is the current version") without a version-detection step become stale quickly as frameworks release major versions. Users following outdated advice waste time troubleshooting version mismatches. The pattern established in `laravel/SKILL.md` and `nextjs-upgrading/SKILL.md` (detect installed version first, then version-conditional guidance) ensures skills remain accurate across framework upgrade cycles.

## Done (This Session)

### Full Survey
Surveyed all 25 remaining skill folders for version-staleness issues (laravel and nextjs-upgrading were already known-good from a prior session).

### Fixed: django/SKILL.md
- **Issue:** Hardcoded "Django 5.0 is current" with no version-detection step; async views section presented as baseline, not version-gated.
- **Fix:** Added "Step 0: Detect installed Django version" (python -m django --version / pip show django / requirements.txt / pyproject.toml). Reframed "Django 5.0 Async Views" section as version-conditional rather than baseline-current.
- **Commit:** b0ac038

### New: odoo-addons/SKILL.md
- Created from scratch following laravel/nextjs-upgrading pattern.
- **Content:** Version detection (odoo-bin --version / __manifest__.py version key), docs fetch step (https://github.com/odoo/documentation; branch-per-major, e.g., 19.0), module structure, ORM patterns, view XML (including attrs/states deprecated in Odoo 17+), security, common pitfalls, and Local Development Environment Setup section (multi-version clone pattern, system deps, odoo.conf template, odoo-bin commands, systemd service template, manifest fields reference).
- **Security note:** Genericized real-world setup content (names, emails, hostnames) with placeholders before committing to public repo.
- **Commit:** b0ac038

### New: frappe-framework/SKILL.md
- Created from scratch following laravel/nextjs-upgrading pattern.
- **Content:** Version detection (bench version), DocType structure, ORM, hooks.py, bench CLI, common pitfalls (permission bypass, N+1 queries, commit behavior in background vs request context).
- **Commit:** b0ac038

### Registration
- Added both new skills (odoo-addons, frappe-framework) to README.md and index.json.
- **Commit:** b0ac038

### Fixed: go-fiber-v3/SKILL.md
- **Issue:** Minor — v3-specific guidance lacked verification that user's go.mod actually has gofiber/fiber v3.
- **Fix:** Added grep go.mod precondition to verify major version before trusting v3-specific guidance.
- **Commit:** 57525df

### Fixed: react-three-fiber/SKILL.md
- **Issue:** Minor — v9/v10-specific examples not conditioned on actual installed version.
- **Fix:** Added grep package.json precondition to verify @react-three/fiber and drei versions before trusting examples.
- **Commit:** 57525df

### Fixed: github-actions-cicd/SKILL.md
- **Issue:** Low priority — pinned Action versions (e.g., actions/checkout@v4) presented as current without caveat.
- **Fix:** Added note that pinned Action versions are illustrative; users should verify latest before production use.
- **Commit:** 1ec2c06

### Fixed: monorepo-scaffold-nextjs-go/SKILL.md
- **Issue:** Low priority — pinned stack versions (Next.js 16+, React 19, Go 1.20+, next-auth v5) presented without version-drift caveat.
- **Fix:** Added note that pinned versions are a snapshot; users should verify current before scaffolding, though structure/patterns remain valid.
- **Commit:** 1ec2c06

### Added: hono/SKILL.md — Migration Notes Section
- **Why:** User pasted actual Hono migration guide content mid-session; prompted a more robust migration reference.
- **Added:** "Migration Notes" section with link to canonical Hono migration guide plus a table of known breaking-change milestones (v2→v3, v3→v4, v4.3.x→v4.4.0 deno.land/x→JSR).
- **Commit:** 056198b

### GitHub Issues
- Filed Thai-language GitHub issues #11 through #15 documenting each unit of work.
- All created-and-closed immediately per established reporting convention in this repo.
- **Commit references:** b0ac038, 57525df, 1ec2c06, 056198b

## Remaining

None. The full version-staleness audit is CLOSED. Every flagged item from the initial survey has been addressed.

## Key Findings and Patterns Established

1. **"Detect installed version dynamically, never hardcode a version as current"**
   - Established by laravel/SKILL.md and nextjs-upgrading/SKILL.md; now the expected standard for ALL version-sensitive framework skills.
   - Apply this pattern when creating or reviewing any skill for a framework with frequent major releases.

2. **Genericization of real-world setup content**
   - When a skill's public repo could leak personal info (names, emails, real hostnames/credentials) via real-world example content, always genericize with placeholders before committing.
   - Established during the odoo-addons setup-section addition.

3. **GitHub issue-per-unit-of-work convention**
   - Create Thai-language issue for each unit of work, close immediately, reference commit hash.
   - Issues #11–#15 follow this pattern on my-skills.

## Blockers

None. Work is complete and verified.

## Set By

Session 2026-08-23 (Boss, Boy, Note personas). Commits: b0ac038, 57525df, 1ec2c06, 056198b on main branch.
