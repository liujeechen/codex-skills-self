---
name: tsd-git-source-editing
description: Safely inspect and edit source files protected by Topscomm TSD or similar Git clean/smudge filters when worktree files appear encrypted but Git objects expose editable plaintext. Use for encrypted firmware repositories; do not use to bypass encryption when the repository lacks an authorized working filter.
---

# TSD Git Source Editing

Use the repository's already-configured Git clean/smudge filter. Never attempt to decrypt TSD data independently or directly overwrite an encrypted worktree file with plaintext.

## Establish the safe path

1. Run `git rev-parse --show-toplevel` and compare it with the user-authorized repository. Do not operate in similarly named legacy directories.
2. Run `git status --short`, `git diff --check`, and a scoped `git diff`. Preserve all existing changes; never use reset or checkout to discard them.
3. Inspect `.gitattributes` or `git check-attr -a -- <path>`. Confirm that Git/TSD filters are configured and that `git show HEAD:<path>` produces plausible source. Stop if the filter is unavailable or Git only returns ciphertext.

## Read plaintext

- For the committed version, use `git show HEAD:<repo-relative-path>`.
- For a modified worktree version, do not fall back to `HEAD`. Run `git hash-object -w -- <path>` to pass the current worktree file through its clean filter, then read that blob with `git show <hash>` or `git cat-file blob <hash>`.
- Treat plaintext temporary files as sensitive. Keep them in the OS temporary directory and delete them in `finally`/cleanup handling.

## Edit without corrupting TSD storage

1. Export the current plaintext version to a temporary UTF-8 source file. Base it on the current worktree-clean blob when the target is already modified.
2. Modify the temporary plaintext with `apply_patch`. Assert that fragile text replacements match exactly once.
3. Install the plaintext with `scripts/install-tsd-plaintext.ps1`. The script writes a plaintext Git blob with `--no-filters`, copies the real index, points only the temporary index at that blob, and calls `checkout-index` so the repository's smudge filter recreates the protected worktree representation.
4. Never use `git hash-object --no-filters` on the encrypted worktree file. It is only for a known plaintext temporary file.

Example:

```powershell
& <skill-dir>/scripts/install-tsd-plaintext.ps1 `
  -RepoRoot (git rev-parse --show-toplevel) `
  -Path 'relative/path/source.c' `
  -PlaintextPath $temporaryPlaintext
```

The helper rejects untracked targets, non-stage-zero index entries, paths outside the repository, and a repository whose real index changes during the operation. It does not stage the result.

## Verify

After every installed edit, run:

```powershell
git status --short
git diff --check
git diff -- <path>
git diff --cached --stat
```

Require a normal plaintext diff with only intended changes. Confirm the real staged state is unchanged unless the user explicitly requested staging. Build or syntax-check in proportion to the change. Remove all temporary plaintext and temporary index files.

If normal `apply_patch` works on a repository-native plaintext file, use it directly; this workflow is specifically for protected files that ordinary patching cannot safely edit.
