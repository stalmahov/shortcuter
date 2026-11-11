#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# HIGH is Bandit's highest severity. Lower findings remain in the JSON report.
mkdir -p reports/static
set +e
bandit -r app --ignore-nosec -f json -o reports/static/bandit.json
scan_status=$?
set -e
if [ "$scan_status" -gt 1 ]; then exit "$scan_status"; fi
python3 - <<'PY'
import json, sys
from pathlib import Path
report = json.loads(Path('reports/static/bandit.json').read_text())
errors = report.get('errors', [])
high = [r for r in report['results'] if r['issue_severity'] == 'HIGH']
print(f"Bandit: {len(report['results'])} findings, {len(high)} HIGH, {len(errors)} scan errors")
for r in high:
    print(f"{r['filename']}:{r['line_number']} {r['test_id']}: {r['issue_text']}")
sys.exit(1 if high or errors else 0)
PY
