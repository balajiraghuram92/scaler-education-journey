#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUNNER_IMAGE="${EXERCISE_RUNNER_IMAGE:-neuralascent-java-runner:dev}"

docker build \
  --file "${PROJECT_DIR}/runner/java/Dockerfile" \
  --tag "${RUNNER_IMAGE}" \
  "${PROJECT_DIR}/runner/java"
