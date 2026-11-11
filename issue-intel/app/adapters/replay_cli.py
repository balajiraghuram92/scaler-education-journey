"""Replay ticket events from the corpus into the webhook endpoint.

Entry: `python -m app.adapters.replay_cli --n 10 --api http://localhost:8010`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay tracker events.")
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--api", default="http://localhost:8010")
    parser.add_argument("--corpus", default=str(ROOT / "synthetic" / "corpus"
                                                / "tracker_export.json"))
    args = parser.parse_args()
    payload = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    keys = [c["key"] for c in payload["tracker_cases"][: args.n]]
    with httpx.Client(timeout=30.0) as client:
        for i, key in enumerate(keys):
            event = "updated" if i % 3 == 1 else "created"
            response = client.post(
                f"{args.api}/webhooks/tracker",
                json={"event": event, "key": key},
            )
            response.raise_for_status()
            print(key, event, response.json())


if __name__ == "__main__":
    main()
