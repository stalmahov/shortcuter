#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Disposable CI database. Never connect pytest to a shared application database.
run_id="${1:?Pass a unique build ID}"
case "$run_id" in *[!0-9]*|'') echo 'Build ID must be numeric' >&2; exit 2;; esac
network="shortcuter-ci-$run_id"
db="shortcuter-ci-db-$run_id"
runner="shortcuter-ci-tests-$run_id"
test_password=$(cat /proc/sys/kernel/random/uuid)
cleanup() {
  docker rm -f "$runner" "$db" >/dev/null 2>&1 || true
  docker network rm "$network" >/dev/null 2>&1 || true
}
# These names belong only to this build. No existing volumes are removed.
trap cleanup EXIT
docker network create "$network" >/dev/null
docker run -d --name "$db" --network "$network" --network-alias ci-db \
  --tmpfs /var/lib/postgresql/data \
  -e POSTGRES_USER=shortcuter -e POSTGRES_DB=shortcuter \
  -e POSTGRES_PASSWORD="$test_password" postgres:16-alpine >/dev/null
ready=0
for attempt in $(seq 1 30); do
  if docker exec "$db" pg_isready -U shortcuter -d shortcuter >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done
if [ "$ready" -ne 1 ]; then echo 'CI database did not become ready' >&2; exit 2; fi
docker cp services/db/schema.sql "$db:/tmp/schema.sql"
docker exec "$db" psql -U shortcuter -d shortcuter -v ON_ERROR_STOP=1 -f /tmp/schema.sql
docker create --name "$runner" --network "$network" -w /work \
  -e PYTHONUNBUFFERED=1 \
  -e DATABASE_URL="postgresql+psycopg://shortcuter:$test_password@ci-db:5432/shortcuter" \
  python:3.11-slim bash -c \
  'pip install -r requirements.txt -r requirements-test.txt && python -m pytest tests/ -v' >/dev/null
docker cp . "$runner:/work"
docker start -a "$runner" || true
state=$(docker inspect -f '{{.State.Status}}' "$runner")
if [ "$state" != exited ]; then echo 'Test container did not exit normally' >&2; exit 2; fi
exit "$(docker inspect -f '{{.State.ExitCode}}' "$runner")"
