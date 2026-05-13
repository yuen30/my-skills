---
name: typescript-fixer
description: Dedicated to resolving TypeScript errors, improving type definitions, and ensuring strict type safety. Use when `tsc` fails, or when refactoring complex interfaces/types.
---

# TypeScript Fixer Workflow

This skill proactively hunts and fixes type mismatches and improves code quality.

## Common Fixes
1. **Formatting**: Fix `string` vs `number` issues in currency/date formatters.
2. **API Types**: Synchronize frontend types with backend JSON responses.
3. **Any-to-Safe**: Replace `any` or `unknown` with precise interfaces.
4. **Null Checks**: Add optional chaining or null guards to prevent runtime crashes.

## Verification
- Run `bun run typecheck` in `webapp` or `frontend`.
- Ensure `tsconfig.json` rules are respected.
- Verify that types in `next-auth.d.ts` match the Session object.

## Tools
- `tsc --noEmit`
- ESLint with TypeScript rules.
