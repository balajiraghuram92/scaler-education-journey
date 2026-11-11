"""Generator entrypoint: python -m synthetic.generate [--seed N]."""
from __future__ import annotations

import argparse
from pathlib import Path

from synthetic.data import SEED_DEFAULT
from synthetic.world import build_world
from synthetic.writers import (
    write_chat_xml,
    write_ground_truth,
    write_legacy_csv,
    write_tracker_json,
)

ROOT = Path(__file__).resolve().parent.parent


def run_generator(seed: int, out_dir: Path) -> None:
    world = build_world(seed)
    write_legacy_csv(world, out_dir / "corpus" / "legacy_cases.csv")
    write_tracker_json(world, out_dir / "corpus" / "tracker_export.json")
    write_chat_xml(world, out_dir / "corpus" / "chat_export.xml")
    write_ground_truth(world, out_dir / "ground_truth")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Tessera synthetic corpus.")
    parser.add_argument("--seed", type=int, default=SEED_DEFAULT)
    args = parser.parse_args()
    run_generator(args.seed, ROOT / "synthetic")
    # Ground truth belongs under evals/, not synthetic/: move it there.
    generated = ROOT / "synthetic" / "ground_truth"
    target = ROOT / "evals" / "ground_truth"
    target.mkdir(parents=True, exist_ok=True)
    for child in sorted(generated.iterdir()):
        (target / child.name).write_bytes(child.read_bytes())
        child.unlink()
    generated.rmdir()
    print(f"corpus written to {ROOT / 'synthetic' / 'corpus'}")
    print(f"ground truth written to {target}")


if __name__ == "__main__":
    main()
