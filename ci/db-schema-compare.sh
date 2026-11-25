#!/usr/bin/env bash
set -euo pipefail
umask 077

source_profile=${1:?Pass the source PostgreSQL connection profile}
target_profile=${2:?Pass the target PostgreSQL connection profile}
if [ "$source_profile" = "$target_profile" ]; then
  echo 'Choose two different database profiles' >&2
  exit 2
fi
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT

dump_schema() {
  PGSERVICE="$1" pg_dump --no-password --schema=public --schema-only --no-owner --no-privileges |
    sed -E '/^-- Dumped (from|by) /d; /^\\(un)?restrict /d' > "$2"
}

if ! dump_schema "$source_profile" "$scratch/source.sql" ||
   ! dump_schema "$target_profile" "$scratch/target.sql"; then
  echo 'Could not read both database schemas' >&2
  exit 2
fi
diff -u "$scratch/target.sql" "$scratch/source.sql"
printf 'Public schemas match: %s and %s\n' "$source_profile" "$target_profile"
