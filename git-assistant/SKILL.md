---
name: git-assistant
description: Automates the entire Git workflow: analyzing changes, generating semantic commit messages, staging files, committing, and pushing to the current branch. Use when the user wants to "sync", "commit and push", or "save changes" to the repository.
---

# Git Assistant Workflow

This skill automates the process of saving and pushing work to a Git repository with high-quality, descriptive commit messages.

## Operational Procedures

Follow these steps sequentially when triggered:

### 1. Research & Analysis
- Run `git status` to identify modified, deleted, and new files.
- Run `git diff HEAD` (and `git diff --staged` if some files are already staged) to understand the technical details of the changes.
- Identify the current branch using `git branch --show-current`.

### 2. Generate Semantic Commit Message
Analyze the diff to create a message following the [Conventional Commits](https://www.conventionalcommits.org/) standard:
- **Format**: `<type>(<scope>): <description>`
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.
- **Scope**: The specific module or directory affected (e.g., `webapp`, `frontend`, `services/watcher`).
- **Body**: Provide a concise bulleted list of "What" and "Why" for significant changes.

### 3. Execution
- **Stage**: Run `git add .` (unless the user specifies files).
- **Commit**: Execute `git commit -m "<generated_message>"`.
  - *Note*: If commit fails due to pre-commit hooks, explain the errors to the user.
- **Push**: Execute `git push origin <current_branch>`.

### 4. Verification
- Run `git status` to confirm the working tree is clean.
- Provide a brief summary of the commit hash and the branch it was pushed to.

## Best Practices
- **Never commit secrets**: Check the diff for any accidental inclusion of API keys, `.env` files, or credentials.
- **Clarity**: Ensure the commit message is helpful for future developers.
