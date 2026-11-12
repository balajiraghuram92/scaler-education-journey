"""Parity checker: call the .NET API and the Python API with the same request
and diff status code plus normalised JSON.

Usage:
    python tools/parity.py --routes tools/parity_routes.txt [--ignore timestamp,traceId]
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import urllib.request

DOTNET_BASE = os.environ.get("PARITY_DOTNET_BASE", "http://127.0.0.1:5000")
PYTHON_BASE = os.environ.get("PARITY_PYTHON_BASE", "http://127.0.0.1:8081")


def _call(base: str, method: str, path: str, body: object, headers: dict[str, str]) -> tuple[int, object]:
    data = None
    req_headers = dict(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:  # noqa: S310 - local dev tool
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return exc.code, raw


def _normalize(value: object, ignore: set[str]) -> object:
    if isinstance(value, dict):
        return {k: _normalize(v, ignore) for k, v in value.items() if k not in ignore}
    if isinstance(value, list):
        return [_normalize(v, ignore) for v in value]
    return value


def _render(status: int, payload: object) -> list[str]:
    return [f"status: {status}", *json.dumps(payload, indent=2, sort_keys=True, default=str).splitlines()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff .NET API vs Python API responses.")
    parser.add_argument("--routes", required=True, help="File with 'METHOD path [json body]' lines.")
    parser.add_argument("--ignore", default="timestamp,traceId,traceid,appliedMigrationsCount,occurredAt",
                        help="Comma-separated volatile field names to ignore.")
    parser.add_argument("--api-key", default=os.environ.get("API_KEY", ""))
    parser.add_argument("--dotnet-base", default=DOTNET_BASE)
    parser.add_argument("--python-base", default=PYTHON_BASE)
    args = parser.parse_args(argv)
    ignore = {name.strip() for name in args.ignore.split(",") if name.strip()}
    headers = {}
    if args.api_key:
        headers["x-api-key"] = args.api_key

    with open(args.routes, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() and not ln.strip().startswith("#")]

    failures = 0
    for line in lines:
        parts = line.split(None, 2)
        method = parts[0].upper()
        path = parts[1]
        body = json.loads(parts[2]) if len(parts) > 2 else None
        dotnet_status, dotnet_payload = _call(args.dotnet_base, method, path, body, headers)
        python_status, python_payload = _call(args.python_base, method, path, body, headers)
        left = _render(dotnet_status, _normalize(dotnet_payload, ignore))
        right = _render(python_status, _normalize(python_payload, ignore))
        if left == right:
            print(f"OK   {method} {path}")
        else:
            failures += 1
            print(f"DIFF {method} {path}")
            for diff_line in difflib.unified_diff(left, right, fromfile="dotnet", tofile="python", lineterm=""):
                print(f"  {diff_line}")
    print(f"{len(lines) - failures}/{len(lines)} routes match.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
