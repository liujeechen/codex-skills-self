#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 SOURCE REPO MANAGED BACKUP" >&2
  exit 64
fi

source_path=$1
repo_path=$2
managed_path=$3
backup_path=$4

fail() {
  echo "PRECHECK_FAIL: $*" >&2
  exit 1
}

[ -e "$source_path" ] || fail "source does not exist: $source_path"
[ ! -L "$source_path" ] || fail "source is already a symbolic link: $source_path"
[ -d "$source_path" ] || fail "source is not a directory: $source_path"
[ -f "$source_path/SKILL.md" ] || fail "SKILL.md is missing: $source_path/SKILL.md"
[ -r "$source_path/SKILL.md" ] || fail "SKILL.md is not readable: $source_path/SKILL.md"

case "$managed_path" in
  "$repo_path"/*) ;;
  *) fail "managed path is not inside repository: $managed_path" ;;
esac

[ ! -e "$repo_path" ] && [ ! -L "$repo_path" ] || fail "repository path already exists: $repo_path"
[ ! -e "$managed_path" ] && [ ! -L "$managed_path" ] || fail "managed path already exists: $managed_path"
[ ! -e "$backup_path" ] && [ ! -L "$backup_path" ] || fail "backup path already exists: $backup_path"

echo "PRECHECK_OK"
echo "source=$source_path"
echo "repo=$repo_path"
echo "managed=$managed_path"
echo "backup=$backup_path"
find "$source_path" -maxdepth 2 -printf '%M %p\n' | sort
