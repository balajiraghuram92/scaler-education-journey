"""Allow-list tests: AssetImport is never attempted (pure)."""
from __future__ import annotations

import pytest

from app.agents.candidates import candidate_eligible

ALLOWLIST = ["VersionControl", "Localization", "UiState"]


def test_eligible_when_all_conditions_hold() -> None:
    assert candidate_eligible("UiState", 0.9, True, ALLOWLIST, 0.7)


def test_assetimport_never_attempted() -> None:
    for confidence in (0.0, 0.7, 1.0):
        for opt_in in (False, True):
            assert not candidate_eligible(
                "AssetImport", confidence, opt_in, ALLOWLIST, 0.7
            )


def test_low_confidence_rejected() -> None:
    assert not candidate_eligible("UiState", 0.69, True, ALLOWLIST, 0.7)


def test_no_opt_in_rejected() -> None:
    assert not candidate_eligible("UiState", 0.9, False, ALLOWLIST, 0.7)


@pytest.mark.parametrize("module", ALLOWLIST)
def test_each_allowlisted_module_can_qualify(module: str) -> None:
    assert candidate_eligible(module, 1.0, True, ALLOWLIST, 0.7)
