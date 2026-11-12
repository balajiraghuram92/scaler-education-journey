"""Auto-Route decision: pure function, no I/O, no model calls.

Scores are on the 1-5 judge scale; the default project threshold is 4
(a score below it needs review).

Inputs: the QPS score (None when the judge fell back), the project's QPS
threshold, and the deterministic check results from MT Optimize (if any).

Outputs: a RouteDecision with needs_review and machine-readable reasons.

Failure behaviour: there is none — every input maps to a decision. A missing
score routes to review (unverified quality must see a human), as does any
failed deterministic check regardless of score.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RouteDecision:
    needs_review: bool
    reasons: list[str] = field(default_factory=list)


def route(
    *,
    qps_score: int | None,
    qps_threshold: int,
    checks: dict[str, bool] | None = None,
) -> RouteDecision:
    """Decide needs_review: below-threshold score, missing score, or any
    failed deterministic check. Reasons name every trigger."""
    reasons: list[str] = []
    if qps_score is None:
        reasons.append("qps_unavailable")
    elif qps_score < qps_threshold:
        reasons.append("qps_below_threshold")
    for name, ok in sorted((checks or {}).items()):
        if not ok:
            reasons.append(f"check_failed:{name}")
    return RouteDecision(needs_review=bool(reasons), reasons=reasons)
