#!/usr/bin/env sh
# Runs the trusted tests against the learner's files and writes a JUnit XML report to the
# same location the Java runner uses, so the API parses both the same way.
set -eu

cd /workspace
export PYTHONPATH=/workspace
mkdir -p target/surefire-reports

exec python -m pytest \
  -q \
  -p no:cacheprovider \
  --tb=short \
  --color=no \
  -o junit_family=xunit1 \
  --junitxml=target/surefire-reports/TEST-pytest.xml \
  tests
