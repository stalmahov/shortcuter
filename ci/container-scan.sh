#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports/static
case "${1:-}" in
  bandit)
    image=python:3.11-slim
    command='python -m pip install -q -r ci/requirements-static.txt >&2 && bash ci/bandit.sh'
    ;;
  gitleaks)
    image=ghcr.io/gitleaks/gitleaks:v8.30.0
    command='sh ci/gitleaks.sh'
    ;;
  *) echo 'Usage: bash ci/container-scan.sh bandit|gitleaks' >&2; exit 2 ;;
esac
# Stream files: avoids checkout-path mismatches when the agent uses a host Docker socket.
# Include every tracked file, even if ignored, and new non-ignored source files.
# Runtime .env and generated reports are not repository inputs.
# Requires Git, Docker, tar and bash. No application or DB is started.
git ls-files --cached --others --exclude-standard -z |
 tar --null -T - -cf - |
 docker run --rm -i --entrypoint sh "$image" -c '
  mkdir -p /work && cd /work && tar -xf - || exit 2
  tool=$1
  scan_command=$2
  sh -c "$scan_command" >&2
  status=$?
  if [ -f "reports/static/$tool.json" ]; then
    cat "reports/static/$tool.json"
  else
    echo "No report produced" >&2
    exit 2
  fi
  exit "$status"
 ' sh "$1" "$command" > "reports/static/$1.json"
