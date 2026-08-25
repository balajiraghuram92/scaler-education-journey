#!/usr/bin/env sh
set -eu

exercise_id="${1:-}"
variant="${2:-}"
source_override="${3:-}"

if [ -z "$exercise_id" ] || [ -z "$variant" ]; then
  echo "Usage: $0 java-lld-oop3-point-threedpoint starter|solution [source-root]" >&2
  exit 2
fi

if [ "$exercise_id" != "java-lld-oop3-point-threedpoint" ]; then
  echo "Unsupported exercise: $exercise_id" >&2
  exit 2
fi

case "$variant" in
  starter|solution) ;;
  *)
    if [ -z "$source_override" ]; then
      echo "Unsupported source variant: $variant (expected starter or solution)" >&2
      exit 2
    fi
    ;;
esac

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
exercise_root="$repo_root/exercises/java/java-lld/oop-3/point-threedpoint"
if [ -n "$source_override" ]; then
  if [ ! -d "$source_override" ]; then
    echo "Custom source root does not exist: $source_override" >&2
    exit 2
  fi
  source_root=$(CDPATH= cd -- "$source_override" && pwd)
  source_label="$variant (custom source)"
else
  source_root="$exercise_root/$variant/src/main/java"
  source_label="$variant"
fi
workspace=$(mktemp -d "${TMPDIR:-/tmp}/neuralascent-java-${exercise_id}.XXXXXX")
keep_workspace="${KEEP_WORKSPACE:-0}"
outer_timeout="${JAVA_RUNNER_TIMEOUT:-120}"
container_name="neuralascent-java-$(basename "$workspace")"

cleanup() {
  docker rm -f "$container_name" >/dev/null 2>&1 || true
  if [ "$keep_workspace" = "1" ]; then
    echo "Retained execution workspace: $workspace" >&2
  else
    rm -rf "$workspace"
  fi
}
trap cleanup EXIT INT TERM

mkdir -p "$workspace/src/main/java" "$workspace/src/test/java"
cp "$exercise_root/pom.xml" "$workspace/pom.xml"
cp -R "$source_root/." "$workspace/src/main/java/"
cp -R "$exercise_root/tests/src/test/java/." "$workspace/src/test/java/"

echo "Exercise: $exercise_id"
echo "Source variant: $source_label"
echo "Workspace: $workspace"

set +e
timeout --signal=TERM --kill-after=5s "${outer_timeout}s" \
  docker run --rm --init \
    --name "$container_name" \
    --network bridge \
    --memory="${JAVA_RUNNER_MEMORY:-768m}" \
    --cpus="${JAVA_RUNNER_CPUS:-1.0}" \
    --pids-limit="${JAVA_RUNNER_PIDS:-128}" \
    --mount "type=bind,src=$workspace,dst=/workspace" \
    --mount "type=volume,src=neuralascent-maven-cache,dst=/root/.m2" \
    neuralascent-java-runner:dev
status=$?
set -e

if [ "$status" -eq 124 ] || [ "$status" -eq 137 ]; then
  echo "Java exercise execution timed out or was terminated." >&2
fi

exit "$status"
