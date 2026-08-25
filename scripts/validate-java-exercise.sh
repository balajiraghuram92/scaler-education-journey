#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
exercise_root="$repo_root/exercises/java/java-lld/oop-3/point-threedpoint"
runner="$repo_root/scripts/run-java-exercise.sh"
validation_root=$(mktemp -d "${TMPDIR:-/tmp}/neuralascent-java-validation.XXXXXX")
startup_timeout="${JAVA_RUNNER_TIMEOUT:-120}"
execution_timeout="${JAVA_EXERCISE_TIMEOUT:-20}"

cleanup() {
  rm -rf "$validation_root"
}
trap cleanup EXIT INT TERM

run_case() {
  label="$1"
  expectation="$2"
  timeout_override="$3"
  retain_reports="$4"
  shift 4

  echo
  echo "=== $label ==="
  set +e
  output=$(JAVA_RUNNER_TIMEOUT="$timeout_override" \
    KEEP_WORKSPACE="$retain_reports" \
    TMPDIR="$validation_root" \
    "$runner" "$@" 2>&1)
  status=$?
  set -e
  printf '%s\n' "$output"

  case "$expectation" in
    success)
      if [ "$status" -ne 0 ]; then
        echo "Validation failed: $label expected exit 0, got $status." >&2
        exit 1
      fi
      if ! printf '%s\n' "$output" | grep -q "Tests run: 7"; then
        echo "Validation failed: $label did not report all seven authoritative tests." >&2
        exit 1
      fi
      ;;
    failure)
      if [ "$status" -eq 0 ]; then
        echo "Validation failed: $label expected a non-zero exit." >&2
        exit 1
      fi
      ;;
    timeout)
      if [ "$status" -ne 124 ] && [ "$status" -ne 137 ]; then
        echo "Validation failed: $label expected timeout exit 124 or 137, got $status." >&2
        exit 1
      fi
      if ! printf '%s\n' "$output" | grep -q "timed out or was terminated"; then
        echo "Validation failed: $label did not report a timeout." >&2
        exit 1
      fi
      ;;
    *)
      echo "Unknown validation expectation: $expectation" >&2
      exit 2
      ;;
  esac

  echo "Validated: $label (exit $status)."
}

mkdir -p "$validation_root/compile-error" \
  "$validation_root/behavioral-failure" \
  "$validation_root/timeout"

for fixture in compile-error behavioral-failure timeout; do
  cp -R "$exercise_root/solution/src/main/java/." "$validation_root/$fixture/"
done

# Compile failure: introduce a statement that cannot occur at class scope.
sed -i '/protected int y;/a this is not valid java;' \
  "$validation_root/compile-error/Point.java"

# Behavioral failure: keep the program compilable but change the required output.
sed -i 's/ + y + "]"/ + (y + 1) + "]"/' \
  "$validation_root/behavioral-failure/Point.java"

# Timeout: the first display call never returns; the outer harness must stop it.
sed -i '/public void display()/a while (true) { }' \
  "$validation_root/timeout/Point.java"

run_case "golden solution" success \
  "$startup_timeout" \
  0 \
  java-lld-oop3-point-threedpoint solution

run_case "incomplete starter" failure \
  "$execution_timeout" \
  0 \
  java-lld-oop3-point-threedpoint starter

run_case "compile error" failure \
  "$execution_timeout" \
  0 \
  java-lld-oop3-point-threedpoint compile-error "$validation_root/compile-error"

run_case "behavioral failure" failure \
  "$execution_timeout" \
  1 \
  java-lld-oop3-point-threedpoint behavioral-failure "$validation_root/behavioral-failure"

behavior_workspace=$(printf '%s\n' "$output" | sed -n 's/^Retained execution workspace: //p' | tail -n 1)
if [ -z "$behavior_workspace" ] || [ ! -f "$behavior_workspace/target/surefire-reports/TEST-ThreedPointTest.xml" ]; then
  echo "Validation failed: behavioral failure did not retain a Surefire XML report." >&2
  exit 1
fi
echo "Validated: behavioral failure produced $behavior_workspace/target/surefire-reports/TEST-ThreedPointTest.xml."

run_case "timeout" timeout \
  "$execution_timeout" \
  0 \
  java-lld-oop3-point-threedpoint timeout "$validation_root/timeout"

echo
echo "All Java exercise validation scenarios passed."
