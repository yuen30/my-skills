---
name: Next.js CI Build Caching
description: Expert guidance on configuring CI build caching for Next.js — GitHub Actions, GitLab CI, CircleCI, and other providers to speed up builds.
---

# Next.js CI Build Caching

Expert guidance on configuring CI build caching for Next.js — GitHub Actions, GitLab CI, CircleCI, and other providers to speed up builds.

@doc-version: 16.2.6

## Core Concepts

Next.js เก็บ build cache ไว้ที่ `.next/cache` ซึ่งใช้ร่วมกันระหว่าง builds เพื่อเพิ่มความเร็ว CI workflow ต้อง persist directory นี้ระหว่าง builds

> ถ้าไม่ config → จะเห็น "No Cache Detected" error และ build ช้าลง

## Guidelines

### 1. Vercel

ไม่ต้องทำอะไร — cache ถูก configure อัตโนมัติ

### 2. GitHub Actions

```yaml
# .github/workflows/build.yml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      ${{ github.workspace }}/.next/cache
    # Generate new cache เมื่อ packages หรือ source files เปลี่ยน
    key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx') }}
    # ถ้า source เปลี่ยนแต่ packages ไม่เปลี่ยน → rebuild จาก prior cache
    restore-keys: |
      ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-
```

### 3. GitLab CI

```yaml
# .gitlab-ci.yml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .next/cache/
```

### 4. CircleCI

```yaml
# .circleci/config.yml
steps:
  - save_cache:
      key: dependency-cache-{{ checksum "yarn.lock" }}
      paths:
        - ./node_modules
        - ./.next/cache
```

### 5. Travis CI

```yaml
# .travis.yml
cache:
  directories:
    - $HOME/.cache/yarn
    - node_modules
    - .next/cache
```

### 6. AWS CodeBuild

```yaml
# buildspec.yml
cache:
  paths:
    - 'node_modules/**/*'
    - '.next/cache/**/*'
```

### 7. Netlify

ใช้ [`@netlify/plugin-nextjs`](https://www.npmjs.com/package/@netlify/plugin-nextjs) — จัดการ cache ให้อัตโนมัติ

### 8. Bitbucket Pipelines

```yaml
# bitbucket-pipelines.yml
definitions:
  caches:
    nextcache: .next/cache

pipelines:
  default:
    - step:
        name: Build
        caches:
          - node
          - nextcache
        script:
          - npm ci
          - npm run build
```

### 9. Azure Pipelines

```yaml
# azure-pipelines.yml
- task: Cache@2
  displayName: 'Cache .next/cache'
  inputs:
    key: next | $(Agent.OS) | yarn.lock
    path: '$(System.DefaultWorkingDirectory)/.next/cache'
```

### 10. Heroku

```json
// package.json
{
  "cacheDirectories": [".next/cache"]
}
```

### 11. Jenkins (Pipeline)

```groovy
// Jenkinsfile
stage("Build") {
  steps {
    writeFile file: "next-lock.cache", text: "$GIT_COMMIT"

    cache(caches: [
      arbitraryFileCache(
        path: ".next/cache",
        includes: "**/*",
        cacheValidityDecidingFile: "next-lock.cache"
      )
    ]) {
      sh "npm run build"
    }
  }
}
```

## Complete GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'npm'

      - name: Cache Next.js build
        uses: actions/cache@v4
        with:
          path: |
            ~/.npm
            ${{ github.workspace }}/.next/cache
          key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx') }}
          restore-keys: |
            ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-

      - run: npm ci
      - run: npm run build
      - run: npm run lint
```

## Quick Reference

| CI Provider | Cache Path | Key Strategy |
|-------------|-----------|--------------|
| Vercel | อัตโนมัติ | — |
| GitHub Actions | `.next/cache` | package-lock + source hash |
| GitLab CI | `.next/cache/` | branch slug |
| CircleCI | `./.next/cache` | lockfile checksum |
| Travis CI | `.next/cache` | directory-based |
| AWS CodeBuild | `.next/cache/**/*` | path-based |
| Bitbucket | `.next/cache` | custom cache definition |
| Azure Pipelines | `.next/cache` | lockfile-based |
| Heroku | `.next/cache` | `cacheDirectories` in package.json |
| Jenkins | `.next/cache` | GIT_COMMIT hash |

## สรุป

1. **Cache `.next/cache`** ระหว่าง builds — เร็วขึ้นอย่างมาก
2. **Key strategy** — ใช้ lockfile + source hash เพื่อ invalidate เมื่อจำเป็น
3. **Restore keys** — fallback ไป partial cache เมื่อ source เปลี่ยน
4. **Vercel** — ไม่ต้องทำอะไร (อัตโนมัติ)
5. **ถ้าไม่ config** → "No Cache Detected" error + build ช้า
