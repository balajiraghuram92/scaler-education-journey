"""Rendering tests: withholding, ACL visibility, wrong-module alert (pure)."""
from __future__ import annotations

from app.governance.entitlements import Entitlements, is_visible
from app.pipeline.render import withhold_claims, wrong_module_alert


def test_withhold_claims_drops_cites_of_removed_evidence() -> None:
    claims = [
        {"text": "a", "cites": ["E1"]},
        {"text": "b", "cites": ["E1", "E2"]},
        {"text": "c", "cites": ["E3"]},
    ]
    kept, withheld = withhold_claims(claims, {"E1", "E2"})
    assert [c["text"] for c in kept] == ["a", "b"]
    assert withheld == 1


def test_withhold_claims_keeps_everything_when_all_visible() -> None:
    claims = [{"text": "a", "cites": ["E1"]}]
    kept, withheld = withhold_claims(claims, {"E1"})
    assert kept == claims
    assert withheld == 0


def test_is_visible_matrix() -> None:
    ent = Entitlements({"UiState"}, {"Support"}, 0)
    assert is_visible("UiState", "Support", 0, ent)
    assert not is_visible("UiState", "Support", 1, ent)  # too restricted
    assert not is_visible("VersionControl", "Support", 0, ent)  # wrong module
    assert not is_visible("UiState", "SE", 0, ent)  # wrong department
    assert is_visible("VersionControl,UiState", "SE,Support", 0, ent)  # overlap


def test_wrong_module_alert_requires_hidden_module() -> None:
    s2 = {"wrong_module": True, "predicted_module": "AssetImport", "confidence": 0.9}
    alert = wrong_module_alert(s2, {"UiState"})
    assert alert is not None
    assert alert["predicted_module"] == "AssetImport"
    assert alert["actions"] == ["request_access", "notify_owner"]


def test_wrong_module_alert_hidden_when_visible() -> None:
    s2 = {"wrong_module": True, "predicted_module": "UiState", "confidence": 0.9}
    assert wrong_module_alert(s2, {"UiState"}) is None
    assert wrong_module_alert({"wrong_module": False}, set()) is None
