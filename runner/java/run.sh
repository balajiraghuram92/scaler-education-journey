#!/usr/bin/env sh
set -eu

cd /workspace

exec mvn \
  --batch-mode \
  --no-transfer-progress \
  test
