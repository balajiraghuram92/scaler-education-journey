#!/usr/bin/env bash
# Batch-verify every exercise wired in the batch3/batch4/batch1 porting session.
# For each exercise: assembles solution+tests (expect BUILD SUCCESS) and
# starter+tests (expect BUILD FAILURE / test failures) into temp dirs and runs
# `mvn test`, printing one summary line per variant.
#
# Usage: bash info/.notes/verify-new-exercises.sh
# Run from the repo root.

set -u

EXERCISES=(
  exercises/java/java-lld/design-patterns/strategy-video-streaming
  exercises/java/java-lld/design-patterns/observer-task-assignment
  exercises/java/java-lld/design-patterns/observer-weather-monitoring
  exercises/java/java-lld/design-patterns/observer-stock-price-alerts
  exercises/java/java-lld/applied-machine-coding/tictactoe-undo-and-win-check
  exercises/java/java-lld/applied-machine-coding/tictactoe-win-check
  exercises/java/java-lld/design-patterns/factory-board-game
  exercises/java/java-lld/design-patterns/factory-database-connection
  exercises/java/java-lld/solid-principles/cloud-provider-adapter-integration
  exercises/java/java-lld/applied-machine-coding/hotel-get-rooms
  exercises/java/java-lld/applied-machine-coding/hotel-add-rooms
  exercises/java/java-lld/applied-machine-coding/hotel-book-rooms
  exercises/java/java-lld/applied-machine-coding/hotel-generate-invoice
  exercises/java/java-lld/advanced-collections/generic-comparison
  exercises/java/java-lld/advanced-collections/generic-pair
  exercises/java/java-lld/advanced-collections/generic-print-array
  exercises/java/java-lld/advanced-collections/generic-linked-list
  exercises/java/java-lld/advanced-collections/bounded-generics-find-max
  exercises/java/java-lld/advanced-collections/process-sentences
  exercises/java/java-lld/advanced-collections/count-unique-words
  exercises/java/java-lld/advanced-collections/filter-fruits
  exercises/java/java-lld/advanced-collections/distinct-numbers
  exercises/java/java-lld/advanced-collections/sort-animals-by-length
  exercises/java/java-lld/advanced-collections/student-sorter
  exercises/java/java-lld/advanced-collections/frequency-counter
  exercises/java/java-lld/advanced-collections/group-anagrams
  exercises/java/java-lld/advanced-collections/unique-persons
  exercises/java/java-lld/oop-4/scaler-learning-platform-users
  exercises/java/java-lld/oop-3/media-file-player
  exercises/java/java-lld/oop-3/vehicle-renting
  exercises/java/java-lld/oop-2/shape-hierarchy
  exercises/java/java-lld/concurrency/synchronized-counter
  exercises/java/java-lld/concurrency/thread-basics-adder-subtractor
  exercises/java/java-lld/concurrency/big-factorial-thread
  exercises/java/java-lld/concurrency/image-painter-executors
  exercises/java/java-lld/concurrency/movie-ticket-reservation
  exercises/java/java-lld/concurrency/train-reservation-per-class-locks
  exercises/java/java-lld/design-patterns/singleton-file-config
  exercises/java/java-lld/design-patterns/prototype-configuration
  exercises/java/java-lld/design-patterns/prototype-invoice
  exercises/java/java-lld/design-patterns/prototype-user
  exercises/java/java-lld/design-patterns/builder-database-configuration
  exercises/java/java-lld/design-patterns/builder-query
  exercises/java/java-lld/design-patterns/builder-message
  # Stage 2 (2026-10-01): Splitwise and BookMyShow ports
  exercises/java/java-lld/applied-machine-coding/splitwise-create-delete-group
  exercises/java/java-lld/applied-machine-coding/splitwise-manage-group-members
  exercises/java/java-lld/applied-machine-coding/bms-book-ticket
)

REPO_ROOT="$(pwd)"
PASS=0
FAIL=0
FAILED_LIST=()

run_variant() {
  local ex_dir="$1" variant="$2"
  local tmp
  tmp=$(mktemp -d)
  cp "$REPO_ROOT/$ex_dir/pom.xml" "$tmp/"
  cp -r "$REPO_ROOT/$ex_dir/$variant/src" "$tmp/"
  mkdir -p "$tmp/src/test"
  cp -r "$REPO_ROOT/$ex_dir/tests/src/test/java" "$tmp/src/test/"
  ( cd "$tmp" && mvn -q -B test > mvn_output.log 2>&1 )
  local status=$?
  local summary
  summary=$(grep -E "Tests run" "$tmp/mvn_output.log" | tail -1)
  echo "$status|$summary|$tmp"
}

for ex in "${EXERCISES[@]}"; do
  if [[ ! -f "$REPO_ROOT/$ex/pom.xml" ]]; then
    echo "SKIP (no pom.xml): $ex"
    continue
  fi

  sol_result=$(run_variant "$ex" "solution")
  sol_status="${sol_result%%|*}"
  rest="${sol_result#*|}"
  sol_summary="${rest%%|*}"
  sol_tmp="${rest##*|}"

  sta_result=$(run_variant "$ex" "starter")
  sta_status="${sta_result%%|*}"
  rest="${sta_result#*|}"
  sta_summary="${rest%%|*}"
  sta_tmp="${rest##*|}"

  ok=true
  if [[ "$sol_status" != "0" ]]; then
    ok=false
    echo "❌ $ex  [SOLUTION FAILED TO PASS]  $sol_summary  (log: $sol_tmp/mvn_output.log)"
  fi
  if [[ "$sta_status" == "0" ]]; then
    ok=false
    echo "⚠️  $ex  [STARTER UNEXPECTEDLY PASSED]  $sta_summary  (log: $sta_tmp/mvn_output.log)"
  fi

  if $ok; then
    echo "✅ $ex  solution: $sol_summary | starter correctly fails"
    PASS=$((PASS+1))
    rm -rf "$sol_tmp" "$sta_tmp"
  else
    FAIL=$((FAIL+1))
    FAILED_LIST+=("$ex")
  fi
done

echo
echo "=== Summary: $PASS passed, $FAIL failed/flagged out of ${#EXERCISES[@]} ==="
if [[ $FAIL -gt 0 ]]; then
  echo "Flagged exercises:"
  for f in "${FAILED_LIST[@]}"; do echo "  - $f"; done
fi
