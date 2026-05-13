---
name: qa-automation
description: Automates end-to-end (E2E) and integration testing using Playwright. Use when writing new test cases, fixing broken tests, or verifying critical user flows like checkout.
---

# QA Automation Workflow

This skill focuses on maintaining high system reliability through automated testing.

## Test Domains
- **Storefront**: Login, Product Search, Add to Cart, Checkout.
- **Admin**: User CRUD, Promotion Config, Log Inspection.
- **API**: Health checks and SAP Mock response verification.

## Testing Standards
1. **Environment**: Run tests against `localhost:3000` (webapp) or `localhost:3003` (frontend).
2. **Setup**: Use `webapp/playwright.config.ts` as the base configuration.
3. **Artifacts**: Store screenshots and traces in `test-results/`.
4. **Smoke Tests**: Run `bun run test:e2e:smoke` for quick verification.

## Best Practices
- **Data Isolation**: Use mock users or unique IDs to prevent test data collision.
- **Wait Strategies**: Prefer `toBeVisible()` over hard-coded timeouts.
- **CI Readiness**: Ensure tests can run headlessly in Bitbucket Pipelines.
