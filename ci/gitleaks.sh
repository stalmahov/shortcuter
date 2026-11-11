#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports/static
# Snapshot mode: works in TeamCity even with server-side checkout (no .git).
# Redaction keeps detected values out of logs and report artifacts.
gitleaks dir . --config .gitleaks.toml --redact --exit-code 1 \
  --report-format json --report-path reports/static/gitleaks.json
