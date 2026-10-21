#!/usr/bin/env bash
# Verifies Python exercises with the real runner image (run inside WSL/Linux with Docker).
#   1. starter/ + solution/ overlay + tests/  -> every test must PASS
#   2. starter/ + tests/                       -> tests must be COLLECTED (no import/syntax error)
#                                                 and at least one must FAIL
# Usage: runner/python/verify-exercise.sh <exercise-dir> [<exercise-dir> ...]
# Exit code is non-zero if any exercise fails verification.
set -uo pipefail

IMAGE="${PYTHON_RUNNER_IMAGE:-neuralascent-python-runner:dev}"
status=0

run_case() { # $1 = workspace dir
    docker run --rm --network none --memory 512m --pids-limit 256 \
        --user "$(id -u):$(id -g)" -e HOME=/tmp \
        -v "$1:/workspace" "$IMAGE" >"$1/.out" 2>&1
    echo $?
}

for dir in "$@"; do
    dir="${dir%/}"
    name="$(basename "$dir")"
    if [ ! -f "$dir/exercise.json" ] || [ ! -d "$dir/tests" ] || [ ! -d "$dir/starter" ] || [ ! -d "$dir/solution" ]; then
        echo "FAIL $name: needs exercise.json, starter/, solution/ and tests/"; status=1; continue
    fi

    tmp="$(mktemp -d)"
    mkdir -p "$tmp/sol" "$tmp/start"
    cp -r "$dir/starter/." "$tmp/sol/"; cp -r "$dir/solution/." "$tmp/sol/"; cp -r "$dir/tests" "$tmp/sol/tests"
    cp -r "$dir/starter/." "$tmp/start/"; cp -r "$dir/tests" "$tmp/start/tests"

    sol_code="$(run_case "$tmp/sol")"
    start_code="$(run_case "$tmp/start")"
    sol_summary="$(tail -n 1 "$tmp/sol/.out")"
    start_summary="$(tail -n 1 "$tmp/start/.out")"

    ok=1
    if [ "$sol_code" != "0" ]; then
        ok=0; echo "FAIL $name: solution does not pass ($sol_summary)"; tail -n 25 "$tmp/sol/.out" | sed 's/^/    /'
    fi
    # pytest exit 1 = tests ran and some failed (wanted); 2/3/4 = collection or usage error; 5 = no tests.
    if [ "$start_code" != "1" ]; then
        ok=0; echo "FAIL $name: starter must import cleanly and fail tests, got exit $start_code ($start_summary)"; tail -n 25 "$tmp/start/.out" | sed 's/^/    /'
    fi
    [ "$ok" = "1" ] && echo "PASS $name: solution [$sol_summary] | starter [$start_summary]" || status=1
    rm -rf "$tmp"
done

exit $status
