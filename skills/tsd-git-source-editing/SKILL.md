---
name: tsd-git-source-editing
description: Safely inspect and edit source files protected by Topscomm TSD, including Windows Git clean/smudge setups and Ubuntu TSDEncryptfs mounts, when worktree files appear encrypted but authorized Git access exposes plaintext. Use for encrypted firmware repositories; do not use to bypass encryption when no authorized plaintext path is available.
---

# TSD Git Source Editing

Use only the environment's authorized plaintext path. On Windows this is commonly a repository Git clean/smudge filter; on Ubuntu it may instead be a `TSDEncryptfs` mount that presents plaintext to Git while ordinary byte readers see `TSZ#`. Never derive keys, independently decrypt TSD data, or directly overwrite an encrypted worktree file with plaintext.

## Establish the safe path

1. Run `git rev-parse --show-toplevel` and compare it with the user-authorized repository. Do not operate in similarly named legacy directories.
2. Run `git status --short`, `git diff --check`, and a scoped `git diff`. Preserve all existing changes; never use reset or checkout to discard them.
3. Identify the authorized protection mechanism:
   - Inspect `.gitattributes`, repository/global Git config, and `git check-attr -a -- <path>` for a Git filter.
   - On Linux, also inspect `findmnt -T <repo>` or `mount` for `TSDEncryptfs` when no Git attribute is present.
   - Require `git show HEAD:<path>` to produce plausible source rather than a `TSZ#` payload. Stop if neither an authorized filter nor an authorized protected mount is present, or if Git only returns ciphertext.
4. Detect both staged and unstaged target changes. Never replace a modified target with its `HEAD` version.

## Read plaintext

- For the committed version, use `git show HEAD:<repo-relative-path>`.
- For a modified worktree version, do not fall back to `HEAD`. Run `git hash-object -w --path=<path> -- <path>` so Git obtains the current logical content through the authorized protection layer, then read that blob with `git cat-file blob <hash>`.
- Treat plaintext temporary files as sensitive. Keep them in the OS temporary directory and delete them in `finally`/cleanup handling.

Linux example:

```bash
repo=$(git rev-parse --show-toplevel)
path='relative/path/source.c'
tmp_plain=$(mktemp "${TMPDIR:-/tmp}/tsd-source.XXXXXX")
trap 'rm -f -- "$tmp_plain"' EXIT

if git diff --quiet -- "$path" && git diff --cached --quiet -- "$path"; then
  git show "HEAD:$path" >"$tmp_plain"
else
  blob=$(git hash-object -w --path="$path" -- "$path")
  git cat-file blob "$blob" >"$tmp_plain"
fi
```

## Edit without corrupting TSD storage

1. Export the current plaintext version to a temporary UTF-8 source file. Base it on the current worktree-clean blob when the target is already modified.
2. Modify the temporary plaintext with `apply_patch`. Assert that fragile text replacements match exactly once.
3. Install the plaintext with the helper for the current OS:
   - Ubuntu/Linux: `scripts/install-tsd-plaintext.sh`
   - Windows/PowerShell: `scripts/install-tsd-plaintext.ps1`

   Both helpers write a known plaintext Git blob with `--no-filters`, copy the real index, point only a temporary index at that blob, and call `checkout-index` so the authorized TSD layer recreates the protected worktree representation.
4. Never use `git hash-object --no-filters` on the encrypted worktree file. It is only for a known plaintext temporary file.

Ubuntu/Linux example:

```bash
<skill-dir>/scripts/install-tsd-plaintext.sh \
  "$(git rev-parse --show-toplevel)" \
  'relative/path/source.c' \
  "$tmp_plain"
```

Windows/PowerShell example:

```powershell
& <skill-dir>/scripts/install-tsd-plaintext.ps1 `
  -RepoRoot (git rev-parse --show-toplevel) `
  -Path 'relative/path/source.c' `
  -PlaintextPath $temporaryPlaintext
```

The helpers reject untracked targets, non-stage-zero index entries, paths outside the repository, and a repository whose real index changes during the operation. They do not stage the result.

## Verify

After every installed edit, run:

```text
git status --short
git diff --check
git diff -- <path>
git diff --cached --stat
```

Require a normal plaintext diff with only intended changes. Confirm the real staged state is unchanged unless the user explicitly requested staging. Build or syntax-check in proportion to the change. Remove all temporary plaintext and temporary index files.

If normal `apply_patch` works on a repository-native plaintext file, use it directly; this workflow is specifically for protected files that ordinary patching cannot safely edit. On `TSDEncryptfs`, tools that use different I/O paths may see different representations, so a successful `rg` or Git read does not authorize direct non-Git overwrite of a `TSZ#` worktree file.
