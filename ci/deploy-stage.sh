#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."

export COMPOSE_FILE=docker-compose.yml:ci/stage-compose.yml
if [ -z "$(docker compose ps -q postgres)" ]; then
  echo 'Existing STAGE PostgreSQL is not running in this Compose project.' >&2
  exit 1
fi

docker compose pull app
docker compose build frontend
docker compose up -d --no-deps app

temporary=lab8-stage-frontend
was_running=$(docker inspect --format '{{.State.Running}}' "$temporary" 2>/dev/null || true)
restore_frontend() {
  docker compose stop frontend || true
  if [ "$was_running" = true ]; then
    docker start "$temporary"
  fi
}

if [ "$was_running" = true ]; then
  docker stop "$temporary"
fi
if docker compose up -d --no-deps frontend; then
  for attempt in 1 2 3 4 5; do
    if docker compose exec -T frontend node -e \
      'fetch("http://127.0.0.1:5173").then(r=>{if(!r.ok)process.exit(1)})'; then
      docker compose ps
      exit 0
    fi
    sleep 2
  done
fi
restore_frontend
exit 1
