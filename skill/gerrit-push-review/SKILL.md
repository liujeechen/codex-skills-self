---
name: gerrit-push-review
description: Push local commits to Gerrit review refs and recover from common Gerrit push blockers. Use when Codex needs to submit the current branch or commit to Gerrit review refs like `refs/for/branch-name`, handle remote-fast-forward rejections, continue or abort interrupted rebases, inspect branch divergence, or explain Gerrit responses such as `no new changes` and missing `Change-Id`.
---

# Gerrit Push Review

Push review changes conservatively. Preserve unrelated working tree changes. Prefer reusing the user's current branch and commit unless there is a clear reason to rebase or rebuild the commit.

## Workflow

1. Inspect repository state before pushing.
   Run:
   ```bash
   git status --short
   git branch --show-current
   git remote -v
   ```
   Confirm whether the worktree is dirty and whether a rebase, cherry-pick, or merge is already in progress.

2. Inspect local vs remote branch position.
   Run:
   ```bash
   git fetch origin <branch>
   git log --oneline --decorate --graph --max-count=12 HEAD origin/<branch>
   ```
   Use this to decide whether the current commit is already based on the remote tip.

3. Push directly to Gerrit when the branch is already in the right shape.
   Run:
   ```bash
   git push origin HEAD:refs/for/<branch>
   ```
   Use this first when the user explicitly asks to push for review.

4. If push fails because remote branch moved, rebase the user commit onto `origin/<branch>`.
   Prefer:
   ```bash
   git rebase --autostash origin/<branch>
   ```
   If a rebase is already in progress, inspect `git status` before doing anything else.

5. If rebase is interrupted but there are no unresolved conflicts, continue it.
   Run:
   ```bash
   git rebase --continue
   ```
   If the rebase is clearly wrong or stuck on the wrong base, abort it:
   ```bash
   git rebase --abort
   ```

6. After rebasing successfully, push again:
   ```bash
   git push origin HEAD:refs/for/<branch>
   ```

## Guardrails

- Do not discard unrelated local modifications.
- Do not use destructive commands like `git reset --hard` unless the user explicitly asks.
- If the worktree contains unrelated changes, prefer `--autostash` or leave those files untouched.
- If a submodule-like path or generated directory is dirty and unrelated, do not stage or revert it.
- If the repository is mid-rebase, resolve that state before interpreting push results.

## Commit Message Formatting

- Summarize concrete changes in the commit body, with one change per line.
- When the body contains multiple changes, prefix them with Chinese sequence markers: `1、`, `2、`, `3、`, and so on.
- When the body contains only one change, write it directly without forcing a sequence number.
- Keep `Change-Id` in its own final paragraph after the change list.

## Interpreting Gerrit Responses

- `no new changes`
  The commit being pushed does not create a new Gerrit review update. Usually the same patch content or same Change-Id state is already present. Check whether the commit was already pushed or whether a new patch set requires a real content change plus `git commit --amend`.

- `fetch first`
  The remote branch moved. Rebase the local commit onto `origin/<branch>` and push again.

- `pushing without Change-Id is deprecated`
  The push may still succeed, but future updates to the same review will be harder. Recommend installing Gerrit's `commit-msg` hook or amending commits with a proper `Change-Id`.

- `interactive rebase in progress`
  The repository is not in a normal state. Finish or abort the rebase before concluding anything about the push.

## When to Read More

Read [references/gerrit-troubleshooting.md](references/gerrit-troubleshooting.md) when:
- Gerrit rejects the push and the error is ambiguous
- a rebase is partially applied and the branch/HEAD state is confusing
- you need a compact decision table for `no new changes`, `fetch first`, or missing `Change-Id`
