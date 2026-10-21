from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScryptParams:
    n: int = 2**14
    r: int = 8
    p: int = 1
    dklen: int = 32


class PasswordHasher:
    """Self-describing salted scrypt hasher (standard library only: hashlib.scrypt, secrets, hmac, base64).

    Stored format: ``scrypt$<n>$<r>$<p>$<salt_b64>$<hash_b64>`` (standard base64).
    """

    def __init__(self, params: ScryptParams = ScryptParams()) -> None:
        raise NotImplementedError("Implement PasswordHasher.__init__")

    def encode(self, raw_password: str) -> str:
        """Fresh 16-byte random salt per call (``secrets.token_bytes``). Empty password -> ValueError."""
        raise NotImplementedError("Implement encode")

    def matches(self, raw_password: str, stored: str) -> bool:
        """Re-derive with the STORED salt and parameters and compare with ``hmac.compare_digest``.

        Never raises: malformed strings, unknown schemes, bad base64 or non-numeric parameters return False.
        """
        raise NotImplementedError("Implement matches")

    def needs_rehash(self, stored: str) -> bool:
        """True if the stored n/r/p differ from this hasher's, or the string is malformed."""
        raise NotImplementedError("Implement needs_rehash")
