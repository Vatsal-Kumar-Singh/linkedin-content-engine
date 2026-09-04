---
description: Stage all new and changed files, commit with a real message, and push to GitHub
---

Save the current state of this project to GitHub.

Steps:
1. Run `git status --porcelain` and `git diff --stat HEAD` to see what changed.
2. Before staging, scan any NEW files for secrets (API keys, tokens, private keys,
   `.env` contents). If anything looks sensitive, STOP and ask the user instead of
   committing it. This repo is PUBLIC.
3. Stage everything with `git add -A`.
4. Commit with a descriptive message summarizing what actually changed — never a
   generic message like "update" or "wip".
5. Push with `git push`.
6. Report the commit hash and a one-line summary of what was saved.

If there is nothing to commit, just say so and stop.

Extra context from the user (optional, may be empty): $ARGUMENTS
