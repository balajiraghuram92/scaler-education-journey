import pytest

from password_hasher import PasswordHasher, ScryptParams

FAST = ScryptParams(n=2**4)  # tiny cost keeps the tests quick; never use in production


def test_same_password_hashes_differently_but_both_verify():
    hasher = PasswordHasher(FAST)
    first = hasher.encode("hunter2")
    second = hasher.encode("hunter2")
    assert first != second
    assert hasher.matches("hunter2", first)
    assert hasher.matches("hunter2", second)


def test_wrong_password_and_unicode():
    hasher = PasswordHasher(FAST)
    stored = hasher.encode("pässwörd-密码")
    assert hasher.matches("pässwörd-密码", stored)
    assert not hasher.matches("passwörd-密码", stored)


def test_stored_format_is_self_describing():
    stored = PasswordHasher(ScryptParams(n=2**4, r=8, p=1)).encode("x1")
    parts = stored.split("$")
    assert parts[:4] == ["scrypt", "16", "8", "1"]
    assert len(parts) == 6


def test_verification_uses_stored_parameters_not_current_ones():
    old = PasswordHasher(ScryptParams(n=2**4))
    new = PasswordHasher(ScryptParams(n=2**5))
    stored = old.encode("hunter2")
    assert new.matches("hunter2", stored)
    assert new.needs_rehash(stored)
    assert not old.needs_rehash(stored)
    assert not new.needs_rehash(new.encode("hunter2"))


@pytest.mark.parametrize(
    "garbage",
    [
        "",
        "plaintext",
        "scrypt$16$8$1$abc",
        "bcrypt$16$8$1$c2FsdA==$aGFzaA==",
        "scrypt$x$8$1$c2FsdA==$aGFzaA==",
        "scrypt$16$8$1$@@@$aGFzaA==",
        "scrypt$16$8$1$c2FsdA==$@@@",
    ],
)
def test_malformed_input_never_raises(garbage):
    hasher = PasswordHasher(FAST)
    assert hasher.matches("hunter2", garbage) is False
    assert hasher.needs_rehash(garbage) is True


def test_tampered_hash_is_rejected():
    hasher = PasswordHasher(FAST)
    stored = hasher.encode("hunter2")
    head, digest = stored.rsplit("$", 1)
    flipped = ("A" if digest[0] != "A" else "B") + digest[1:]
    assert not hasher.matches("hunter2", f"{head}${flipped}")


def test_empty_password_rejected():
    with pytest.raises(ValueError):
        PasswordHasher(FAST).encode("")


def test_params_defaults_and_immutability():
    params = ScryptParams()
    assert (params.n, params.r, params.p, params.dklen) == (2**14, 8, 1, 32)
    with pytest.raises(Exception):
        params.n = 1  # frozen dataclass


def test_default_hasher_round_trips_with_default_cost():
    hasher = PasswordHasher()
    stored = hasher.encode("correct horse")
    assert stored.split("$")[:4] == ["scrypt", "16384", "8", "1"]
    assert hasher.matches("correct horse", stored)
    assert not hasher.needs_rehash(stored)


def test_absurd_attacker_supplied_cost_returns_false_instead_of_raising():
    hasher = PasswordHasher(FAST)
    stored = hasher.encode("hunter2")
    _, _, r, p, salt, digest = stored.split("$")
    hostile = f"scrypt${2**30}${r}${p}${salt}${digest}"
    assert hasher.matches("hunter2", hostile) is False
