import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScryptParams:
    n: int = 2**14
    r: int = 8
    p: int = 1
    dklen: int = 32


class PasswordHasher:
    def __init__(self, params: ScryptParams = ScryptParams()) -> None:
        self._params = params

    @staticmethod
    def _derive(raw_password: str, salt: bytes, params: ScryptParams) -> bytes:
        return hashlib.scrypt(
            raw_password.encode("utf-8"),
            salt=salt,
            n=params.n,
            r=params.r,
            p=params.p,
            dklen=params.dklen,
        )

    def encode(self, raw_password: str) -> str:
        if not raw_password:
            raise ValueError("password must not be empty")
        salt = secrets.token_bytes(16)
        params = self._params
        digest = self._derive(raw_password, salt, params)
        salt_b64 = base64.b64encode(salt).decode("ascii")
        hash_b64 = base64.b64encode(digest).decode("ascii")
        return f"scrypt${params.n}${params.r}${params.p}${salt_b64}${hash_b64}"

    def matches(self, raw_password: str, stored: str) -> bool:
        try:
            scheme, n, r, p, salt_b64, hash_b64 = stored.split("$")
            if scheme != "scrypt":
                return False
            expected = base64.b64decode(hash_b64, validate=True)
            salt = base64.b64decode(salt_b64, validate=True)
            params = ScryptParams(int(n), int(r), int(p), dklen=len(expected))
            actual = self._derive(raw_password, salt, params)
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(actual, expected)

    def needs_rehash(self, stored: str) -> bool:
        parts = stored.split("$")
        if len(parts) != 6 or parts[0] != "scrypt":
            return True
        try:
            base64.b64decode(parts[4], validate=True)
            base64.b64decode(parts[5], validate=True)
        except ValueError:
            return True
        current = self._params
        return parts[1:4] != [str(current.n), str(current.r), str(current.p)]
