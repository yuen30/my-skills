---
description: Commit the currently completed unit of work, push, then comment on and close the related GitHub issue
argument-hint: "[issue-number-or-url] [optional commit message override]"
---

Ship the work just completed in this session. Argument (optional): $ARGUMENTS
- If the first token looks like an issue number or a GitHub issue URL, use that issue.
- Otherwise, use the most recent GitHub issue filed by the Note persona in this session (or the most recent open/closed issue clearly tied to the just-finished task).

Do the following, in order, respecting this project's/user's existing git-safety rules (never `git add -A`/`.`, never amend, never force-push, never skip hooks, only commit the intended scope):

1. Run `git status --short` and `git diff` to see what is staged/unstaged. Identify exactly which files belong to the unit of work just completed (the task discussed immediately before this command was invoked) — do not sweep in unrelated pending changes from other tasks.
2. Stage only those specific files by name.
3. Create a new commit (never amend) with a concise conventional-commit-style message describing why the change was made, ending with:
   Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
4. Push the current branch to its remote. If the branch has no upstream yet, push with `-u origin <current-branch>`. Never force-push.
5. Determine the target repo (`gh repo view --json nameWithOwner` or infer from `git remote -v`) and the target issue (from $ARGUMENTS or the most recent one filed this session).
6. Post a comment on that issue via `gh issue comment <number> --body "..."` in Thai, summarizing: files committed, commit hash/message, and confirmation that it was pushed.
7. If the issue is still open, close it with `gh issue close <number>`. If it was already auto-closed (per this project's Note-persona convention), skip closing and just note that in the comment.
8. Report back concisely: commit hash + message, push result, issue number/URL commented and closed/already-closed.

If at any point the diff for step 1 is ambiguous (e.g. multiple unrelated pending units of work mixed in the working tree), stop and ask the user to confirm the exact file list before staging anything — do not guess broadly.
