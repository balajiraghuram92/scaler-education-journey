#!/usr/bin/env bash
# Runs verify-exercise.sh over every Python exercise (solution passes, starter imports and fails),
# in parallel batches, then prints a summary. Run from the repo root inside WSL/Linux with Docker.
# Usage: runner/python/verify-all.sh [jobs]   (default 4 parallel workers)
set -uo pipefail

JOBS="${1:-4}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

mapfile -t dirs < <(find exercises/python -name exercise.json -printf '%h\n' | sort)
echo "Verifying ${#dirs[@]} exercises with $JOBS workers..."

out="$(mktemp -d)"
printf '%s\n' "${dirs[@]}" | xargs -P "$JOBS" -I{} bash -c 'bash runner/python/verify-exercise.sh "{}" > "'"$out"'/$(echo "{}" | tr / _).log" 2>&1'

pass=$(grep -l '^PASS' "$out"/*.log 2>/dev/null | wc -l)
fail=$(grep -L '^PASS' "$out"/*.log 2>/dev/null | wc -l)
echo "PASS: $pass   FAIL: $fail"
for f in $(grep -L '^PASS' "$out"/*.log 2>/dev/null); do echo "----- $(basename "$f" .log)"; head -n 30 "$f"; done
rm -rf "$out"
[ "$fail" -eq 0 ]
