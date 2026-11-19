#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

squawk --pg-version=16.0 --assume-in-transaction --reporter=gcc services/migrations/*.sql
