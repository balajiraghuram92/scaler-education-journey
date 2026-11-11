"""Generator determinism: same seed twice -> identical bytes."""
from __future__ import annotations

from pathlib import Path

from synthetic.generate import run_generator


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_generator_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    run_generator(seed=20240917, out_dir=first)
    run_generator(seed=20240917, out_dir=second)
    assert _snapshot(first) == _snapshot(second)


def test_generator_writes_all_raw_formats_and_ground_truth(tmp_path: Path) -> None:
    run_generator(seed=1, out_dir=tmp_path)
    assert (tmp_path / "corpus" / "legacy_cases.csv").exists()
    assert (tmp_path / "corpus" / "tracker_export.json").exists()
    assert (tmp_path / "corpus" / "chat_export.xml").exists()
    for name in (
        "duplicates",
        "regressions",
        "outcome_labels",
        "chat_root_cause",
        "injections",
        "wrong_module",
    ):
        assert (tmp_path / "ground_truth" / f"{name}.json").exists()
