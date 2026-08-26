# Gerrit Push Troubleshooting

## Quick checks

Run these first:

```bash
git status
git branch --show-current
git rev-parse --short HEAD
git fetch origin <branch>
git log --oneline --decorate --graph --max-count=12 HEAD origin/<branch>
```

## Decision table

### Case: `git push origin HEAD:refs/for/<branch>` succeeds

- Report the review URL if Gerrit prints one.
- Mention the final pushed commit hash.

### Case: `no new changes`

Likely causes:
- the same commit was already pushed
- the commit content matches an existing patch set closely enough that Gerrit sees nothing new
- the branch is not pointing at the commit the user expected

Checks:
```bash
git show --summary --stat HEAD
git log --oneline --decorate --graph --max-count=6 HEAD origin/<branch>
```

Typical fixes:
- if HEAD is wrong, recover the intended commit first
- if the user wants a new patch set, make a real change and `git commit --amend`
- if the review already exists and no content changed, explain that there is nothing new to upload

### Case: `fetch first`

Cause:
- `origin/<branch>` moved ahead of the local base

Preferred fix:
```bash
git rebase --autostash origin/<branch>
git push origin HEAD:refs/for/<branch>
```

If rebase says one is already in progress:
- inspect `git status`
- continue it if safe: `git rebase --continue`
- abort it if the repo is on the wrong path: `git rebase --abort`

### Case: `pushing without Change-Id is deprecated`

Meaning:
- push may succeed now
- future patch set updates may be awkward

Suggested follow-up:
- install Gerrit's `commit-msg` hook in `.git/hooks/commit-msg`
- use `git commit --amend` after the hook is installed so the commit gains a `Change-Id`

## Rebase recovery

### Detect whether rebase is actually conflicted

Run:
```bash
git status
git ls-files -u
```

Interpretation:
- if `git ls-files -u` is empty, there are no unresolved index conflicts
- the repo may simply be paused in "edit commit during rebase" state

### Continue a clean paused rebase

Run:
```bash
git rebase --continue
```

### Abort a wrong rebase

Run:
```bash
git rebase --abort
```

After aborting, confirm recovery:
```bash
git log --oneline --decorate --graph --max-count=8 HEAD origin/<branch>
```

## Preserving unrelated changes

If unrelated files are dirty:
- do not stage them into the Gerrit commit
- do not revert them
- prefer `git rebase --autostash origin/<branch>` when rebasing

If `--autostash` does not protect the state cleanly, inspect whether the dirty path is unrelated and keep it untouched while resolving the branch state.
