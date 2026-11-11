import pytest

from app.pipeline.auto_route import route

CASES = [
    # (qps_score, threshold, checks, needs_review, reasons)
    (85, 70, {"placeholders_preserved": True}, False, []),
    (70, 70, None, False, []),  # at threshold passes
    (69, 70, None, True, ["qps_below_threshold"]),
    (0, 70, None, True, ["qps_below_threshold"]),
    (None, 70, None, True, ["qps_unavailable"]),
    (None, 70, {"glossary_present": False}, True, ["qps_unavailable", "check_failed:glossary_present"]),
    # Any failed deterministic check routes to review regardless of score.
    (99, 70, {"placeholders_preserved": False}, True, ["check_failed:placeholders_preserved"]),
    (99, 70, {"a": True, "b": False, "c": False}, True, ["check_failed:b", "check_failed:c"]),
    (50, 70, {"a": False}, True, ["qps_below_threshold", "check_failed:a"]),
    (100, 70, {}, False, []),
]


@pytest.mark.parametrize(("score", "threshold", "checks", "needs_review", "reasons"), CASES)
def test_route_table(score, threshold, checks, needs_review, reasons):
    decision = route(qps_score=score, qps_threshold=threshold, checks=checks)
    assert decision.needs_review is needs_review
    assert decision.reasons == reasons
