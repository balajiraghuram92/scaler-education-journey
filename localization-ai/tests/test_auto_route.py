import pytest

from app.pipeline.auto_route import route

CASES = [
    # (qps_score, threshold, checks, needs_review, reasons) on the 1-5 scale.
    (5, 4, {"placeholders_preserved": True}, False, []),
    (4, 4, None, False, []),  # at threshold passes
    (3, 4, None, True, ["qps_below_threshold"]),
    (1, 4, None, True, ["qps_below_threshold"]),
    (None, 4, None, True, ["qps_unavailable"]),
    (None, 4, {"glossary_present": False}, True, ["qps_unavailable", "check_failed:glossary_present"]),
    # Any failed deterministic check routes to review regardless of score.
    (5, 4, {"placeholders_preserved": False}, True, ["check_failed:placeholders_preserved"]),
    (5, 4, {"a": True, "b": False, "c": False}, True, ["check_failed:b", "check_failed:c"]),
    (2, 4, {"a": False}, True, ["qps_below_threshold", "check_failed:a"]),
    (5, 4, {}, False, []),
]


@pytest.mark.parametrize(("score", "threshold", "checks", "needs_review", "reasons"), CASES)
def test_route_table(score, threshold, checks, needs_review, reasons):
    decision = route(qps_score=score, qps_threshold=threshold, checks=checks)
    assert decision.needs_review is needs_review
    assert decision.reasons == reasons
