#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

source_profile=${1:?Pass the reference PostgreSQL connection profile}
target_profile=${2:?Pass the target PostgreSQL connection profile}

echo 'Checking schemas before migration'
if bash ci/db-schema-compare.sh "$source_profile" "$target_profile"; then
  echo 'Public schemas already match; checking Alembic revisions'
else
  compare_status=$?
  if [ "$compare_status" -ne 1 ]; then exit "$compare_status"; fi
fi

echo "Applying migrations to $target_profile"
env -u DATABASE_URL PGSERVICE="$target_profile" python3 -m alembic upgrade head
env -u DATABASE_URL PGSERVICE="$target_profile" python3 -m alembic current

echo 'Checking schemas after migration'
bash ci/db-schema-compare.sh "$source_profile" "$target_profile"
