"""Wrong-module view composition: hidden module -> alert, no evidence (pure)."""
from __future__ import annotations

from app.pipeline.render import withhold_claims, wrong_module_alert


def _viewer_answer(s2: dict, claims: list[dict], visible: set[str]) -> dict:
    """Mirrors render_for_viewer policy without the database."""
    alert = wrong_module_alert(s2, {"UiState"})
    if alert is not None:
        return {"evidence": [], "claims": [], "alert": alert}
    kept, withheld = withhold_claims(claims, visible)
    return {"evidence": sorted(visible), "claims": kept, "withheld": withheld}


def test_hidden_module_yields_alert_and_no_evidence() -> None:
    s2 = {"wrong_module": True, "predicted_module": "AssetImport", "confidence": 0.8}
    claims = [{"text": "secret", "cites": ["E1"]}]
    view = _viewer_answer(s2, claims, {"E1"})
    assert view["evidence"] == []
    assert view["claims"] == []
    assert view["alert"]["actions"] == ["request_access", "notify_owner"]


def test_visible_module_yields_filtered_claims() -> None:
    s2 = {"wrong_module": False, "predicted_module": "UiState", "confidence": 0.9}
    claims = [
        {"text": "open", "cites": ["E1"]},
        {"text": "secret", "cites": ["E2"]},
    ]
    view = _viewer_answer(s2, claims, {"E1"})
    assert [c["text"] for c in view["claims"]] == ["open"]
    assert view["withheld"] == 1
