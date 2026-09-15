---
name: github-publish-skill
description: Safely migrate, commit, and publish an existing Codex Skill to a personal GitHub repository, including the required Chinese commit-message format. Use this skill alone for GitHub-only Skill backup, versioning, migration, publication, synchronization, or push; do not also invoke gerrit-push-review-topscomm unless the user explicitly requests a Topscomm Gerrit operation.
---

# Publish a Codex Skill to GitHub

Migrate one existing Skill into Git management while keeping its default Codex path usable. Preserve data and remote history at every stage.

## Routing Boundary

- This skill owns the complete commit and push workflow when the target is a personal GitHub repository containing Codex Skills.
- Do not invoke `gerrit-push-review-topscomm` merely because this workflow creates or amends a Git commit.
- Use the Gerrit skill only when the user explicitly asks for a Topscomm Gerrit action, such as pushing to `refs/for/<branch>`, updating a Gerrit review, or diagnosing a Gerrit rejection.

## Collect Inputs

Resolve these values before writing anything:

- `skill_name`: directory name under the default Skill root.
- `source`: normally `${CODEX_HOME:-$HOME/.codex}/skills/$skill_name`.
- `repo`: requested local Git repository directory.
- `managed`: requested location of the real Skill inside `repo`.
- `backup`: normally `${source}.backup`.
- `remote_url`: exact user-provided GitHub repository URL.
- `branch`: default to `main` unless the user explicitly requests another branch.

Do not silently invent a different remote, destination layout, Git identity, or backup name. Ask only when a missing value materially changes the result.

## Safety Invariants

- Never use `rm -rf`, `git reset --hard`, `git push --force`, or `git push --force-with-lease`.
- Never delete the backup during the migration task.
- Never place a password or token in a repository file, script, remote URL, shell history, or Git config.
- Never overwrite an existing destination, backup, remote, or unrelated directory.
- Never change global `user.name` or `user.email`. Inspect identity before the first commit. If it is wrong or missing, ask for the desired values and configure them only with `git config --local`.
- Stop if the source is missing, already a symbolic link, lacks `SKILL.md`, or has unexpected structure.
- Treat user-owned files and pre-existing Git history as authoritative.
- Perform each mutation only after its preceding read-only verification succeeds.

## Workflow

### 1. Inspect the Source and Destinations

Use `test`, `ls -ld`, `find`, and `readlink` to verify:

1. `source` exists and is a real directory, not a symbolic link.
2. `source/SKILL.md` is a regular readable file.
3. `repo`, `managed`, and `backup` do not conflict with existing paths.
4. Git identity is available, but do not modify global configuration.

Optionally run the bundled read-only checker:

```bash
scripts/preflight.sh "$source" "$repo" "$managed" "$backup"
```

Stop and report exact findings on any failed check.

### 2. Initialize and Copy

Create `repo` and its requested parent structure, then run `git init` in `repo`. Copy with `cp -a` so modes and directory structure are preserved.

Verify byte-level tree equivalence before continuing:

```bash
diff -qr "$source" "$managed"
```

Do not move the source until this comparison succeeds.

### 3. Create the Initial Commit

Inspect `git status`, stage only the managed Skill path, and compose the message using the required format below. Verify the staged diff before committing:

```bash
git add -- "$managed_relative_path"
git diff --cached --check
git diff --cached --stat
```

Confirm a commit exists and the worktree is clean. If identity is missing or incorrect, stop before committing or amend an unpushed commit after setting repository-local identity.

## GitHub Skill Commit Message Format

Use this structure for commits created while publishing a Skill:

```text
<type>：<concise Chinese subject>

1、<concrete change one>
2、<concrete change two>
```

- Inspect recent repository messages and follow the existing subject convention.
- Use a suitable prefix such as `fix：`, `feat：`, `refactor：`, or `docs：`.
- Summarize concrete changes in the body, with one change per line.
- For multiple changes, use Chinese sequence markers `1、`, `2、`, `3、`, and so on.
- For one change, write it directly without forcing a sequence number.
- Do not put local filesystem paths into the message. Include URLs only when the user supplies a shareable URL or explicitly requests it.

### 4. Preserve the Original and Link Codex

Confirm `backup` still does not exist. Move `source` to `backup`; do not delete it. Create an absolute symbolic link from `source` to `managed`.

Verify all of the following:

- `source` is a symbolic link.
- `readlink -f "$source"` exactly equals the canonical `managed` path.
- `source/SKILL.md` remains readable.
- `diff -qr "$backup" "$source"` reports no differences.

If link creation or validation fails, preserve both copies and report the recoverable state.

### 5. Configure Branch and Remote

Rename the local branch to the requested branch, normally `main`. Inspect `git remote -v` before adding anything.

- If `origin` is absent, add the exact `remote_url`.
- If `origin` already equals `remote_url`, keep it.
- If `origin` differs, stop; never replace it without explicit user approval.

### 6. Inspect and Merge Remote History

Query the remote before pushing:

```bash
git ls-remote "$remote_url"
```

If it is empty, proceed to normal push. If refs exist, fetch the target branch and inspect both trees and the commit graph.

- Stop on path collisions or ambiguous repository layout and explain them.
- If histories share an ancestor, use a normal merge or fast-forward as appropriate.
- If histories are unrelated but contain disjoint desired paths, merge with `--allow-unrelated-histories` only after explicitly reporting that fact.
- Resolve conflicts only when the intended content is unambiguous and within user authorization; otherwise stop.
- Preserve both histories. Never force push.

After merging, verify the combined tree, log, and clean status.

### 7. Authenticate GitHub HTTPS

Prefer GitHub CLI. Check `gh --version` and `gh auth status` first. If `gh` is unavailable, install it only with user approval.

Use browser/device authentication:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh auth status --hostname github.com
```

Give the user only the device URL and one-time device code when interactive authorization is required. Never ask the user to paste a token into chat. Confirm the authenticated GitHub account matches the repository owner before pushing.

### 8. Push Normally

Immediately before push, verify status, log, branch, upstream, and remote URL. Then use:

```bash
git push -u origin "$branch"
```

If authentication is unavailable, stop at this point and preserve the completed local migration. If Git rejects a non-fast-forward update, fetch and re-evaluate; do not force push.

### 9. Final Verification

Fetch the remote branch and verify:

- `repo` is a Git worktree.
- current branch is the requested branch.
- upstream is `origin/$branch`.
- local HEAD equals the remote-tracking branch.
- worktree is clean.
- `origin` exactly equals the requested URL for fetch and push.
- `managed/SKILL.md` is readable.
- `source` resolves exactly to `managed`.
- `backup` still exists.
- backup and managed Skill content match unless later intentional changes were made and committed.

Report the actual repository path, Skill path, symlink target, backup path, identity scope, branch, upstream, remote, relevant commit IDs, merge result, push result, and worktree status.

## Recovery Rules

- Before the source move: leave the original untouched and report any partial repository creation.
- After the source move but before link success: do not remove either copy; recreate the link only after checking exact paths.
- After local commit but before push: retain the local commit and backup; authentication failure is not data loss.
- After fetch or merge conflict: show status and conflicting paths; do not abort, reset, or discard changes without explicit approval.
- If the user interrupts the workflow, re-inspect all state before resuming because earlier commands may have partially completed.

## Bundled Script

Use `scripts/preflight.sh` for the initial read-only filesystem checks. It deliberately performs no creation, move, link, Git commit, remote modification, authentication, or push.
