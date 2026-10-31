# Skill consolidation for token economy
Status: done — updated 2026-10-31

## Goal
Fewer, non-overlapping skills with references/; personas reference only existing skills.

## Done
- 37 → 15 skills: abe-framework, abe-ui, abe-data, ci-cd, project-structure, find-skills, web-research (+ docker, redis, rabbitmq, http-status-codes, monorepo-scaffold-nextjs-go, project-memory, context7-auto-research, ship, my-agent).
- scripts/check.py + .githooks/pre-commit guard frontmatter, links, index.json, persona refs, untracked skill files.
- install.sh replaces + prunes skills (manifest), installs parked personas to ~/.claude/agents-disabled only.
- Disabled plugins: unity, figma, zoom-plugin, qt-development-skills, fastly-agent-toolkit, activecampaign.

## Next
- Verify skill selection in a real session (headless `claude -p` test was inconclusive).
- Decide on vercel (37 skills, overlaps abe-framework) and postman (12 skills, API hook) plugins.
