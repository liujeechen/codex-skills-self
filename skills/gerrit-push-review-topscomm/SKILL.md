---
name: gerrit-push-review-topscomm
description: Create, amend, and push Topscomm Git commits with the required Chinese commit-message body and Gerrit Change-Id, while preserving unrelated worktree changes and recovering from Gerrit blockers. Always use when a user in Codex asks to commit code or changes with phrases such as “提交代码”, “给我提交”, “提交刚才的改动”, “commit代码”, “commit changes”, “创建提交”, or asks to amend a commit, push to Gerrit refs/for, rebase before review, or diagnose Gerrit responses. A request to commit does not authorize push.
---

# Topscomm Gerrit Commit and Review

Handle local commits and Gerrit review conservatively. Preserve unrelated worktree changes. Never push unless the user explicitly requests it.

## Local Commit Workflow

Use this workflow whenever the user asks to commit code, even if Gerrit or this skill is not named.

1. Inspect repository state:
   ```bash
   git status --short
   git branch --show-current
   git diff --cached --stat
   ```
   Check for an interrupted rebase, cherry-pick, or merge before changing the index.

2. Resolve the commit scope from the active task and actual diff. Treat phrases such as “刚才的改动” as only the files changed for that task. Do not stage unrelated pre-existing modifications, generated files, or untracked files.

3. Review the target diff before staging. Stage explicit paths, then verify the staged diff:
   ```bash
   git diff -- <path>...
   git add <path>...
   git diff --cached --check
   git diff --cached --stat
   ```
   If nothing is staged, stop and explain rather than creating an empty commit.

4. Compose a Topscomm commit message using the required format below. Inspect recent repository messages when the title convention is unclear.

5. Create the local commit. A commit-only request ends here; do not fetch, rebase, or push.

6. Verify the result:
   ```bash
   git show -s --format='%H%n%n%B' HEAD
   git show --stat --oneline -1
   git status --short
   ```
   Report the commit hash, complete message, included files, and remaining unrelated changes.

## Topscomm Commit Message Format

Use this structure:

```text
<type>：<concise Chinese subject>

1、<concrete change one>
2、<concrete change two>

Change-Id: I<40 lowercase hexadecimal characters>
```

- Prefer the repository's existing subject style. Use a suitable prefix such as `fix：`, `feat：`, `refactor：`, or `docs：` when the surrounding history uses typed subjects.
- Summarize concrete changes in the body, with one change per line.
- For multiple changes, use Chinese sequence markers `1、`, `2、`, `3、`, and so on.
- For one change, write it directly without forcing a sequence number.
- Keep `Change-Id` in its own final paragraph after the change list. It must be the final message paragraph.
- Prefer the repository's executable `.git/hooks/commit-msg` hook to generate `Change-Id`.
- If no hook is available, generate a new unique value in the form `I` plus 40 lowercase hexadecimal characters, and include it during commit creation.
- When amending an existing Gerrit review, preserve its existing `Change-Id`; never generate a replacement unless the user explicitly wants a new review.
- Do not put local filesystem report paths into the message. Include report URLs only when the user supplies a shareable URL or explicitly requests it.

## Amend Workflow

When the user asks to correct the latest commit message or add missing formatting:

1. Inspect `git show -s --format='%H%n%B' HEAD` and the current worktree.
2. Preserve the existing `Change-Id` when present.
3. Use `git commit --amend` without staging unrelated worktree changes.
4. Verify and report the new commit hash because amend replaces the old commit.
5. Do not push unless explicitly requested.

## Gerrit Push Workflow

Only use network operations when the user explicitly asks to push or submit for review.

1. Inspect state and remotes:
   ```bash
   git status --short
   git branch --show-current
   git remote -v
   ```

2. Inspect local versus remote branch position:
   ```bash
   git fetch origin <branch>
   git log --oneline --decorate --graph --max-count=12 HEAD origin/<branch>
   ```

3. Push the existing commit to Gerrit when its base is correct:
   ```bash
   git push origin HEAD:refs/for/<branch>
   ```

4. If the remote branch moved, prefer:
   ```bash
   git rebase --autostash origin/<branch>
   git push origin HEAD:refs/for/<branch>
   ```

5. If a rebase is already in progress, inspect status first. Continue only when conflicts are resolved; abort only when the rebase is clearly wrong.

## Guardrails

- Never stage all files with `git add .`, `git add -A`, or broad globs when unrelated changes exist.
- Never discard, restore, stash, or commit unrelated user changes merely to obtain a clean worktree.
- Never use destructive commands such as `git reset --hard` unless explicitly requested.
- Do not infer push authorization from “提交代码” or “commit”; in this skill those phrases mean create a local commit only.
- Do not amend an earlier user commit unless the user asks to fix that commit or the current task just created it and verification shows its message violates this skill.
- If generated documents should remain local, use local excludes only when authorized; do not silently modify project `.gitignore`.

## Gerrit Responses

- `no new changes`: The same patch or `Change-Id` state likely already exists. Check review history before amending.
- `fetch first`: Rebase the local commit onto the current remote branch, preserving unrelated changes.
- Missing `Change-Id`: Install or use the Gerrit `commit-msg` hook, then amend while preserving the patch content.
- `interactive rebase in progress`: Resolve, continue, or abort the existing rebase before interpreting push results.

Read [references/gerrit-troubleshooting.md](references/gerrit-troubleshooting.md) when a Gerrit rejection is ambiguous, a rebase state is confusing, or detailed recovery guidance is required.
