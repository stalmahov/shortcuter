#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = --docker ]; then
  tar -cf - ci/sql-check.sh ci/requirements-sql.txt services/migrations |
    docker run --rm -i python:3.11-slim sh -ec '
      mkdir /work
      cd /work
      tar -xf -
      pip install -q -r ci/requirements-sql.txt
      bash ci/sql-check.sh
    '
  exit
fi

squawk --pg-version=16.0 --assume-in-transaction --reporter=gcc services/migrations/*.sql
echo 'SQL migration check passed'
