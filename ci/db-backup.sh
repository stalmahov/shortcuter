#!/usr/bin/env bash
set -euo pipefail
umask 077

backup_dir=${1:?Pass a private backup directory outside the checkout}
[[ -d "$backup_dir" && -w "$backup_dir" ]]
: "${PGSERVICE:?Set PGSERVICE to the PostgreSQL connection profile}"

server_version=$(psql -XAt --no-password -c 'SHOW server_version_num')
server_major=$((server_version / 10000))
dump_major=$(pg_dump --version | sed -E 's/^.* ([0-9]+)\..*$/\1/')
restore_major=$(pg_restore --version | sed -E 's/^.* ([0-9]+)\..*$/\1/')
if [[ "$dump_major" != "$server_major" || "$restore_major" != "$server_major" ]]; then
  echo "Use pg_dump and pg_restore from PostgreSQL $server_major for this backup" >&2
  exit 2
fi

backup=$(mktemp "$backup_dir/shortcuter-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
trap 'rm -f -- "$backup"' EXIT
pg_dump --no-password --format=custom --file="$backup"
pg_restore --list "$backup" >/dev/null
final_path="$backup.dump"
mv -- "$backup" "$final_path"
printf 'Database backup verified: %s (%s bytes)\n' "$(basename "$final_path")" "$(wc -c < "$final_path" | tr -d ' ')"
