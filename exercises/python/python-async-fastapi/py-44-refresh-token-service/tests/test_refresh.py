import hashlib
import threading

import pytest

from refresh import GraceReuse, InvalidRefreshToken, RefreshTokenService, ReuseDetected


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def internal_state(svc) -> str:
    """repr of every attribute that holds data (skips the clock and the lock)."""
    parts = []
    for name, value in vars(svc).items():
        if callable(value) or "lock" in name.lower():
            continue
        parts.append(repr(value))
    return "\n".join(parts)


def test_rotation_chain_gives_fresh_tokens():
    svc = RefreshTokenService(clock=Clock())
    t1 = svc.login("alice")
    t2 = svc.rotate(t1)
    t3 = svc.rotate(t2)
    assert len({t1, t2, t3}) == 3, "every rotation must produce a new token"
    assert len(t1) >= 43, "tokens should come from secrets.token_urlsafe(32)"
    assert svc.login("alice") != t1, "each login starts a new family with a new token"


def test_only_hashes_are_stored():
    svc = RefreshTokenService(clock=Clock())
    t1 = svc.login("alice")
    t2 = svc.rotate(t1)
    state = internal_state(svc)
    assert t1 not in state and t2 not in state, "plaintext tokens must never be stored"
    assert hashlib.sha256(t1.encode()).hexdigest() in state, "the SHA-256 hex digest must be what is stored"
    assert hashlib.sha256(t2.encode()).hexdigest() in state


def test_reuse_revokes_whole_family():
    svc = RefreshTokenService(clock=Clock())
    t1 = svc.login("alice")
    t2 = svc.rotate(t1)
    with pytest.raises(ReuseDetected):
        svc.rotate(t1)
    with pytest.raises(InvalidRefreshToken) as info:
        svc.rotate(t2)
    assert str(info.value) == "invalid" and not isinstance(info.value, (ReuseDetected, GraceReuse)), (
        "the newest token of a revoked family is simply invalid"
    )


def test_grace_window_does_not_revoke():
    clock = Clock()
    svc = RefreshTokenService(grace_s=5, clock=clock)
    t1 = svc.login("alice")
    t2 = svc.rotate(t1)
    clock.t += 3
    with pytest.raises(GraceReuse):
        svc.rotate(t1)
    assert svc.rotate(t2), "a grace replay must not revoke the family"
    clock.t += 10
    with pytest.raises(ReuseDetected):
        svc.rotate(t1)


def test_zero_grace_means_any_replay_is_reuse():
    svc = RefreshTokenService(grace_s=0.0, clock=Clock())
    t1 = svc.login("alice")
    svc.rotate(t1)
    with pytest.raises(ReuseDetected):
        svc.rotate(t1)


def test_token_ttl_and_family_max_age():
    clock = Clock()
    svc = RefreshTokenService(ttl_s=100, family_max_age_s=250, clock=clock)
    t = svc.login("alice")
    clock.t = 99
    t = svc.rotate(t)
    clock.t = 198
    t = svc.rotate(t)
    clock.t = 240
    t = svc.rotate(t)  # token age 42 and family age 240 are both inside their limits
    clock.t = 260
    with pytest.raises(InvalidRefreshToken, match="expired"):  # token age 20 is fine: only the family limit trips
        svc.rotate(t)
    other = RefreshTokenService(ttl_s=100, family_max_age_s=1000, clock=clock)
    old = other.login("bob")
    clock.t += 150
    with pytest.raises(InvalidRefreshToken, match="expired"):
        other.rotate(old)


def test_unknown_token_is_invalid():
    svc = RefreshTokenService(clock=Clock())
    with pytest.raises(InvalidRefreshToken) as info:
        svc.rotate("nope")
    assert str(info.value) == "invalid"
    assert issubclass(ReuseDetected, InvalidRefreshToken) and issubclass(GraceReuse, InvalidRefreshToken)


def test_families_are_independent():
    svc = RefreshTokenService(clock=Clock())
    a1 = svc.login("alice")
    b1 = svc.login("alice")  # a second device
    a2 = svc.rotate(a1)
    with pytest.raises(ReuseDetected):
        svc.rotate(a1)
    assert svc.rotate(b1), "reuse in one family must not revoke another family"
    with pytest.raises(InvalidRefreshToken):
        svc.rotate(a2)


def test_revoke_user():
    svc = RefreshTokenService(clock=Clock())
    t = svc.login("alice")
    t_other_device = svc.login("alice")
    bob = svc.login("bob")
    assert svc.revoke_user("alice") == 2, "returns the number of families revoked"
    for token in (t, t_other_device):
        with pytest.raises(InvalidRefreshToken):
            svc.rotate(token)
    assert svc.rotate(bob), "other users are unaffected"
    assert svc.revoke_user("nobody") == 0


def test_concurrent_rotation_has_exactly_one_winner():
    svc = RefreshTokenService(clock=Clock())
    token = svc.login("alice")
    barrier = threading.Barrier(20)
    results = []

    def worker():
        barrier.wait(timeout=5)
        try:
            results.append(("ok", svc.rotate(token)))
        except InvalidRefreshToken as exc:
            results.append((type(exc).__name__, None))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert len(results) == 20, "every thread must finish"
    winners = [kind for kind, _ in results if kind == "ok"]
    assert len(winners) == 1, f"exactly one rotation may succeed, got {len(winners)}"
    losers = [kind for kind, _ in results if kind != "ok"]
    assert len(losers) == 19 and "ReuseDetected" in losers  # later losers may see the already-revoked family
