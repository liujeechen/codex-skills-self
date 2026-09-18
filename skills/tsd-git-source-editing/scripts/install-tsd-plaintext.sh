#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 REPO_ROOT REPO_RELATIVE_PATH PLAINTEXT_FILE" >&2
    exit 64
}

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

[ "$#" -eq 3 ] || usage

repo_input=$1
relative_path=$2
plaintext_input=$3

[ -d "$repo_input" ] || fail "repository directory does not exist: $repo_input"
[ -f "$plaintext_input" ] || fail "plaintext file does not exist: $plaintext_input"

repo_input=$(realpath -e -- "$repo_input")
repository=$(git -C "$repo_input" rev-parse --show-toplevel 2>/dev/null) || \
    fail "not a Git repository: $repo_input"
repository=$(realpath -e -- "$repository")
[ "$repository" = "$repo_input" ] || \
    fail "REPO_ROOT is not the repository top level: $repo_input (actual: $repository)"

plaintext_file=$(realpath -e -- "$plaintext_input")
[ -f "$plaintext_file" ] || fail "plaintext path is not a regular file: $plaintext_file"

case "$relative_path" in
    ""|/*|../*|*/../*|*/..|.|./*|*/./*)
        fail "unsafe repository-relative path: $relative_path"
        ;;
esac

target_path=$(realpath -m -- "$repository/$relative_path")
case "$target_path" in
    "$repository"/*) ;;
    *) fail "target resolves outside repository: $target_path" ;;
esac
[ "$plaintext_file" != "$target_path" ] || \
    fail "plaintext input must be a separate temporary file, not the protected worktree target"
[ "$(LC_ALL=C head -c 4 -- "$plaintext_file")" != "TSZ#" ] || \
    fail "plaintext input starts with the TSD ciphertext marker TSZ#"

index_entries=()
while IFS= read -r -d '' entry; do
    index_entries+=("$entry")
done < <(git -C "$repository" ls-files --stage -z -- "$relative_path")
[ "${#index_entries[@]}" -gt 0 ] || fail "target is not tracked: $relative_path"
[ "${#index_entries[@]}" -eq 1 ] || \
    fail "target has multiple index entries, possibly an unresolved merge: $relative_path"

index_meta=${index_entries[0]%%$'\t'*}
read -r mode object_id stage extra <<<"$index_meta"
[ -z "${extra:-}" ] || fail "unexpected index metadata for: $relative_path"
[ "$stage" = "0" ] || fail "target is not a stage-zero index entry: $relative_path"
case "$mode" in
    100644|100755) ;;
    *) fail "unsupported target mode $mode for $relative_path" ;;
esac
case "$object_id" in
    ''|*[!0-9a-fA-F]*) fail "unexpected index object id for: $relative_path" ;;
esac
case "${#object_id}" in
    40|64) ;;
    *) fail "unexpected index object id length for: $relative_path" ;;
esac

real_index=$(git -C "$repository" rev-parse --git-path index)
case "$real_index" in
    /*) ;;
    *) real_index="$repository/$real_index" ;;
esac
real_index=$(realpath -e -- "$real_index")
[ -f "$real_index" ] || fail "real Git index not found: $real_index"
index_hash_before=$(sha256sum -- "$real_index" | awk '{print $1}')

temporary_index=$(mktemp "${TMPDIR:-/tmp}/tsd-index.XXXXXX")
cleanup() {
    rm -f -- "$temporary_index"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

cp -- "$real_index" "$temporary_index"

blob_hash=$(git -C "$repository" hash-object -w --no-filters -- "$plaintext_file")
case "$blob_hash" in
    ''|*[!0-9a-fA-F]*) fail "failed to create plaintext Git blob" ;;
esac
case "${#blob_hash}" in
    40|64) ;;
    *) fail "unexpected Git object id: $blob_hash" ;;
esac

GIT_INDEX_FILE="$temporary_index" git -C "$repository" update-index \
    --cacheinfo "$mode,$blob_hash,$relative_path"
GIT_INDEX_FILE="$temporary_index" GIT_OPTIONAL_LOCKS=0 \
    git -C "$repository" diff --cached --check -- "$relative_path"

index_hash_pre_checkout=$(sha256sum -- "$real_index" | awk '{print $1}')
[ "$index_hash_pre_checkout" = "$index_hash_before" ] || \
    fail "the real Git index changed during preparation; refusing to update the worktree"

GIT_INDEX_FILE="$temporary_index" git -C "$repository" checkout-index -f -- "$relative_path"

index_hash_after=$(sha256sum -- "$real_index" | awk '{print $1}')
[ "$index_hash_after" = "$index_hash_before" ] || \
    fail "the real Git index changed unexpectedly; inspect the repository before continuing"

echo "Installed plaintext through the authorized Git/TSD path without staging: $relative_path"
