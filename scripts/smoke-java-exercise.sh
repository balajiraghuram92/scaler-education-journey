#!/usr/bin/env bash
set -Eeuo pipefail

API_CONTAINER="${API_CONTAINER:-studytracker-api}"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:5000}"
ENV_FILE="${ENV_FILE:-/etc/studytracker/api.env}"
EXERCISE_ID="java-lld-oop3-point-threedpoint"

fail() {
    printf '[exercise-smoke] ERROR: %s\n' "$*" >&2
    exit 1
}

command -v docker >/dev/null 2>&1 || fail "docker is required."
command -v python3 >/dev/null 2>&1 || fail "python3 is required for safe JSON encoding."
[ -f "${ENV_FILE}" ] || fail "Missing environment file: ${ENV_FILE}"

api_key="$(sed -n 's/^API_KEY=//p' "${ENV_FILE}" | tail -n 1)"
[ -n "${api_key}" ] || fail "API_KEY is missing from ${ENV_FILE}."

export SMOKE_API_BASE_URL="${API_BASE_URL}"
export SMOKE_API_CONTAINER="${API_CONTAINER}"
export SMOKE_API_KEY="${api_key}"

python3 - <<'PY'
import json
import os
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

base_url = os.environ["SMOKE_API_BASE_URL"].rstrip("/")
container = os.environ["SMOKE_API_CONTAINER"]
api_key = os.environ["SMOKE_API_KEY"]
exercise_id = "java-lld-oop3-point-threedpoint"
metadata_timeout_seconds = 30
exercise_timeout_seconds = 180

solution_files = [
    "src/main/java/Point.java",
    "src/main/java/ThreedPoint.java",
]
expected_evidence = {
    "point-x",
    "point-y",
    "point-display-signature",
    "point-display-output",
    "threedpoint-inheritance",
    "threedpoint-override",
    "threedpoint-output",
}


def fail(message):
    print(f"[exercise-smoke] ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def request(method, path, payload=None, timeout_seconds=30):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json", "x-api-key": api_key}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request_value = Request(f"{base_url}{path}", data=body, headers=headers, method=method)
    try:
        with urlopen(request_value, timeout=timeout_seconds) as response:
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8"))
    except HTTPError as error:
        try:
            details = json.loads(error.read().decode("utf-8"))
        except Exception:
            details = {}
        title = details.get("title", "request failed")
        fail(f"{method} {path} returned HTTP {error.code}: {title}")
    except URLError:
        fail(f"{method} {path} could not reach the loopback API.")


def read_solution(relative_path):
    container_path = f"/app/exercises/{exercise_id}/solution/{relative_path}"
    try:
        result = subprocess.run(
            ["docker", "exec", container, "cat", container_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        fail("The trusted golden solution could not be read from the API container.")
    return result.stdout.decode("utf-8")


metadata_status, metadata = request(
    "GET",
    f"/api/exercises/{exercise_id}",
    timeout_seconds=metadata_timeout_seconds,
)
if metadata_status != 200 or metadata.get("id") != exercise_id:
    fail("Exercise metadata smoke check failed.")
if "solution" in json.dumps(metadata, ensure_ascii=False).lower():
    fail("Exercise metadata exposed a solution marker.")

files = [
    {"path": relative_path, "content": read_solution(relative_path)}
    for relative_path in solution_files
]
status, result = request(
    "POST",
    f"/api/exercises/{exercise_id}/run",
    {"files": files, "clientRequestId": "phase4-production-smoke"},
    timeout_seconds=exercise_timeout_seconds,
)

if status != 200:
    fail(f"Exercise execution returned HTTP {status}.")
if result.get("status") != "success":
    fail("Golden solution did not return success.")

summary = result.get("summary") or {}
if summary.get("total") != 7 or summary.get("passed") != 7:
    fail("Golden solution did not produce 7/7 passed tests.")

evidence = result.get("evidence") or []
evidence_by_id = {item.get("id"): item for item in evidence}
if set(evidence_by_id) != expected_evidence:
    fail("Golden solution evidence IDs did not match the trusted manifest.")
if any(item.get("status") != "passed" for item in evidence_by_id.values()):
    fail("Golden solution evidence was not completely passed.")

print("[exercise-smoke] metadata ok; golden execution success; evidence 7/7 passed")
PY
