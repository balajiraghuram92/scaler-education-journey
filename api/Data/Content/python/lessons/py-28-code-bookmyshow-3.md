# Code BookMyShow 3: Users, Passwords and Expiry

The last third of a booking system is where "works in the demo" turns into "survives production": passwords must be stored so a database leak is not a credential leak, abandoned holds must stop blocking seats, and every id arriving from outside must be proven real before you write it. Interviewers use these small details (salted hashes, `default` versus `onupdate`, lazy expiry) to see whether you have shipped a service or only drawn one.

## Concepts Covered

### The signup service and the bugs that hide in plumbing

A layered backend keeps persistence in a repository and rules in a service that receives its collaborators through the constructor. Two plumbing bugs show up constantly in reviews.

First, a constructor that accepts a dependency but never stores it: `self.password_hasher` does not exist, and the failure is an `AttributeError` at the first `sign_up` call, not at construction. Python does not auto-assign parameters; use a dataclass or assign explicitly. Second, a repository method that returns a query **object** instead of a row. A `Query` or `Select` object is always truthy, so `if existing:` rejects every signup, including brand-new emails. Execute the statement: `scalars(...).first()` returns the row or `None`.

```python
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session


class DuplicateEmailError(ValueError):
    pass


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_email(self, email: str) -> "User | None":
        stmt = select(User).where(User.email == email.lower())
        return self._session.scalars(stmt).first()      # a row or None, never a Select

    def save(self, user: "User") -> "User":
        self._session.add(user)
        self._session.flush()                           # assigns user.id
        return user


class UserService:
    def __init__(self, user_repository: UserRepository, password_hasher: "PasswordHasher") -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher           # forgetting this line is the classic bug

    def sign_up(self, email: str, password: str) -> "User":
        if self.user_repository.find_by_email(email) is not None:
            raise DuplicateEmailError(email)
        user = User(email=email.lower(), password_hash=self.password_hasher.encode(password))
        return self.user_repository.save(user)
```

Note `is not None` rather than truthiness, which is robust to objects that define `__bool__` or `__len__`. A unique index on `users.email` is still the real guard against two concurrent signups; the service check just gives a friendly error.

> **Pitfall:** the same "check, then insert" shape as the seat race. Catch `IntegrityError` from the unique index and translate it to `DuplicateEmailError`.

### Password storage: salt, slow hashing, constant-time compare

A plain deterministic hash (`sha256(password)`) has three problems. Equal passwords give equal hashes, so one cracked account exposes every account that shares it. Precomputed rainbow tables apply to everyone. And SHA-256 is fast by design, so a GPU tries billions of guesses per second. The cure is a **random per-password salt** plus a **deliberately expensive** key derivation function (KDF).

The standard library has two usable KDFs: `hashlib.scrypt` (memory-hard) and `hashlib.pbkdf2_hmac` (CPU-hard only). Store everything needed to verify, including the parameters, in one self-describing string so you can raise the cost later.

```python
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
    """Encoded format: scrypt$n$r$p$salt_b64$hash_b64"""

    def __init__(self, params: ScryptParams = ScryptParams()) -> None:
        self._params = params

    @staticmethod
    def _derive(raw: str, salt: bytes, p: ScryptParams) -> bytes:
        return hashlib.scrypt(raw.encode("utf-8"), salt=salt, n=p.n, r=p.r, p=p.p, dklen=p.dklen)

    def encode(self, raw_password: str) -> str:
        salt = secrets.token_bytes(16)                  # fresh salt on every call
        p = self._params
        digest = self._derive(raw_password, salt, p)
        b64 = lambda b: base64.b64encode(b).decode("ascii")
        return f"scrypt${p.n}${p.r}${p.p}${b64(salt)}${b64(digest)}"

    def matches(self, raw_password: str, stored: str) -> bool:
        try:
            scheme, n, r, p, salt_b64, hash_b64 = stored.split("$")
            if scheme != "scrypt":
                return False
            expected = base64.b64decode(hash_b64)
            params = ScryptParams(int(n), int(r), int(p), dklen=len(expected))
            actual = self._derive(raw_password, base64.b64decode(salt_b64), params)
        except ValueError:
            return False
        return hmac.compare_digest(actual, expected)    # constant-time comparison

    def needs_rehash(self, stored: str) -> bool:
        parts = stored.split("$")
        return parts[:4] != ["scrypt", str(self._params.n), str(self._params.r), str(self._params.p)]


hasher = PasswordHasher()
first = hasher.encode("hunter2")
second = hasher.encode("hunter2")
print(first == second)                                  # False: different salts
print(hasher.matches("hunter2", first), hasher.matches("wrong", first))
```

```text
False
True False
```

Because the salt differs per call, you can **never** verify a login by computing `encode(login_password) == stored`. Re-encoding makes a new salt and a different string. Verification re-derives with the **stored** salt and parameters (`matches`), and compares with `hmac.compare_digest` so the comparison time does not leak how many leading bytes matched.

On parameters: the defaults above are a minimum for illustration. OWASP's current guidance starts around `n = 2**17` with `r = 8`, `p = 1` for scrypt (which needs a larger `maxmem` argument than the default 32 MiB cap) or at least 600,000 iterations for `pbkdf2_hmac("sha256", ...)`. Tune to roughly 100 ms per hash on your hardware.

In production prefer a maintained library: `argon2-cffi` (Argon2id, the current OWASP first choice) or `bcrypt`. Both generate their own salt, emit a self-describing string, and are reviewed by cryptographers; hand-rolled formats are easy to get subtly wrong. With `bcrypt`, `hashpw(raw, gensalt())` and `checkpw(raw, stored)` mirror the `encode`/`matches` pair above, but only the first 72 bytes of the password count (depending on the version it truncates or raises), so pre-hash long passphrases deliberately or choose Argon2.

```python
# Production variant (third-party, pip install argon2-cffi)
from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

ph = Argon2Hasher()
stored = ph.hash("hunter2")
try:
    ph.verify(stored, "hunter2")
    if ph.check_needs_rehash(stored):
        stored = ph.hash("hunter2")          # upgrade on successful login
except VerifyMismatchError:
    pass
```

### Timestamps: `default` versus `onupdate`

`created_at` and `updated_at` look trivial and fail in three classic ways. `default` runs when a row is **inserted** and `onupdate` runs when the row is **updated**; both accept a callable that SQLAlchemy calls at flush time. Passing a call result freezes one value at import:

```python
from datetime import datetime, timezone
import time


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


frozen = datetime.now(timezone.utc)      # what default=datetime.now(timezone.utc) captures
time.sleep(0.01)
print(frozen == utc_now(), frozen < utc_now())   # False True: every new row would carry the old time
```

```python
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class Booking(BaseModel):
    __tablename__ = "bookings"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
```

Pass `utc_now`, not `utc_now()`. Use `datetime.now(timezone.utc)`: `datetime.utcnow()` is deprecated since 3.12 and returns a naive value that silently compares wrong against aware ones. Remember that SQLite drops the timezone on read, while PostgreSQL's `timestamptz` keeps it, so normalise at your boundary.

`onupdate` fires only when an `UPDATE` statement is emitted for **that row**. Appending a `Payment` to `booking.payments` changes `payments.booking_id` and leaves the `bookings` row untouched, so `last_modified_at` does not move. If you need that, touch the parent explicitly. `server_default=func.now()` plus a database trigger is the alternative when non-ORM writers also update the table.

### Lazy expiry of soft locks

A held seat must free itself if the user never pays. A background sweeper works but is extra infrastructure. **Lazy expiry** re-evaluates at read time: a `BLOCKED` seat older than the hold window counts as available when the next booking attempt looks at it.

```python
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum, auto

HOLD = timedelta(minutes=15)


class ShowSeatStatus(Enum):
    AVAILABLE = auto()
    BLOCKED = auto()
    BOOKED = auto()


@dataclass
class ShowSeat:
    seat_label: str
    status: ShowSeatStatus = ShowSeatStatus.AVAILABLE
    blocked_at: datetime | None = None


def is_bookable(seat: ShowSeat, now: datetime, hold: timedelta = HOLD) -> bool:
    if seat.status is ShowSeatStatus.AVAILABLE:
        return True
    return (
        seat.status is ShowSeatStatus.BLOCKED
        and seat.blocked_at is not None
        and now - seat.blocked_at > hold
    )


def block_seats(seats: list[ShowSeat], now: datetime) -> None:
    for seat in seats:                                  # check everything first
        if not is_bookable(seat, now):
            raise RuntimeError(f"Seat {seat.seat_label} is not available")
    for seat in seats:                                  # then act
        seat.status = ShowSeatStatus.BLOCKED
        seat.blocked_at = now


t0 = datetime(2026, 11, 1, 14, 0, tzinfo=timezone.utc)
c4 = ShowSeat("C4")
block_seats([c4], t0)
print(c4.status.name, is_bookable(c4, t0 + timedelta(minutes=14)), is_bookable(c4, t0 + timedelta(minutes=19)))
print("stored status at 2:19 PM:", c4.status.name)
```

```text
BLOCKED False True
stored status at 2:19 PM: BLOCKED
```

The trade-off is visible in the last line: the stored status still says `BLOCKED` at 2:19 PM, because nothing rewrote the row. Reports, dashboards and "seats left" counters that read the column directly will under-count availability until someone tries to book. A seat nobody tries to rebook stays stale indefinitely. Pair lazy expiry with a cheap periodic sweep (or compute availability with the same expression in SQL) if other readers exist.

Crucially, the expiry check must sit **inside the same atomic step** as the claim. Fold it into the compare-and-set from the previous lesson, with `cutoff = utc_now() - HOLD`:

```python
from sqlalchemy import and_, or_, update

claimable = or_(
    ShowSeat.status == ShowSeatStatus.AVAILABLE,
    and_(ShowSeat.status == ShowSeatStatus.BLOCKED, ShowSeat.blocked_at < cutoff),
)
stmt = update(ShowSeat).where(ShowSeat.id.in_(ids), claimable).values(
    status=ShowSeatStatus.BLOCKED, blocked_at=utc_now()
)
```

### Validating foreign keys at the service layer

Accepting `region_id` and writing `Theatre(region_id=region_id)` relies on the database foreign key to reject bad ids, producing an opaque `IntegrityError` and, on SQLite without the pragma, no error at all. The convention across a codebase should be: look up the referenced entity through its repository, raise a domain `NotFoundError`, then use it. That also lets the service attach the object, not just an integer.

```python
class NotFoundError(LookupError):
    pass


class TheatreService:
    def __init__(self, theatre_repository, region_repository) -> None:
        self.theatre_repository = theatre_repository
        self.region_repository = region_repository

    def add_theatre(self, name: str, region_id: int):
        region = self.region_repository.find_by_id(region_id)
        if region is None:
            raise NotFoundError(f"region {region_id} does not exist")
        return self.theatre_repository.save(Theatre(name=name, region=region))
```

The lookup-then-insert gap is harmless here because regions are rarely deleted, and the foreign key remains the backstop. For hot paths, rely on the constraint and translate the exception.

## Practical Backend Scenario

An FDE onboards a ticketing client whose support chatbot (an LLM with tools) can "create an account and hold seats". The tools call your service. If signup stores unsalted SHA-256, a leaked database lets an attacker recover the passwords people reuse elsewhere. If seat holds never expire, the chatbot's retries leave inventory permanently blocked after each abandoned conversation. Salted slow hashing, lazy expiry with a 15-minute window, and validated ids are what keep an agent-driven workflow from corrupting production data.

## Practice Loop

1. Implement `PasswordHasher` with `hashlib.scrypt`. Assert that two encodings of one password differ, that `matches` accepts the right password and rejects a wrong one and a tampered string, and measure the time of one `encode`.
2. Add `needs_rehash` and prove that a hash made with weaker parameters is flagged. Write the login flow that re-encodes on success.
3. Re-implement the same pair with `bcrypt` or `argon2-cffi` in a scratch project and compare the stored strings.
4. Run the `utc_now` versus frozen-default snippet, then write a test with a fake clock that proves `last_modified_at` changes on update but not when only a related row is added.
5. Implement `is_bookable` and `block_seats` with an injected `now`, and test at 14, 15 and 16 minutes. Decide whether the boundary is `>` or `>=` and document it.
6. Write `UserService.sign_up` with an in-memory repository and a stub hasher. Test duplicate emails, case differences and that the hasher dependency is actually used.

## Evidence of Understanding

- You can explain why equal passwords must produce different stored hashes, and what the salt and the work factor each defend against.
- You can say why login verification must not call `encode` and compare, and what `hmac.compare_digest` is for.
- You can state why `bcrypt` or `argon2` are preferred to a hand-rolled `scrypt` or `pbkdf2_hmac` format, and what remains your responsibility (parameters, rehash on login, length limits).
- You can explain `default` versus `onupdate`, why a callable is required, and why a related-row change does not touch the parent's timestamp.
- You can describe the stored-state staleness of lazy expiry and how to keep it race-safe.
- You can name the convention for validating foreign ids and why a returned query object breaks truthiness checks.

## Interview Questions to Rehearse

### Q: How do you store passwords?

With a slow, salted, adaptive KDF, ideally Argon2id (or bcrypt/scrypt) from a maintained library, storing the algorithm, parameters, salt and hash in one string. Verify by re-deriving with the stored salt and compare in constant time. Rehash on successful login when parameters are outdated. Never use a fast hash such as SHA-256 alone, and never encrypt passwords reversibly.

### Q: Why does hashing the same password twice give different outputs, and how then do you verify?

Each call generates a new random salt that is embedded in the output. To verify, extract the stored salt and parameters, derive the hash from the login attempt, and compare. Comparing a fresh `encode` against the stored value almost never matches.

### Q: What do `default` and `onupdate` do on a column, and what is the common mistake?

`default` supplies the value at insert and `onupdate` at update, both per row at flush. The mistake is passing `datetime.now(timezone.utc)` instead of a function, which evaluates once at import and stamps every row with process start time.

### Q: Why check seat expiry lazily instead of with a scheduled job?

It needs no extra infrastructure and no scan of the table, and expired holds are cleared exactly when someone wants the seat. The cost is that stored status is stale until re-evaluated, so other readers must apply the same rule, and the check must be atomic with the claim to avoid a new race.

### Q: Your `find_by_email` returns a `Query`. What breaks?

A query object is truthy, so `if existing_user:` is always true and every signup is rejected. Execute it with `.first()` or `.scalar_one_or_none()` and compare with `None`.

## Common Pitfalls

- Storing `sha256(password)` or a global-salt hash, or comparing hashes with `==`.
- Verifying a login by re-encoding the attempt.
- Choosing scrypt or PBKDF2 parameters from a tutorial and never revisiting them.
- `default=datetime.now(...)` (called) instead of the function, and naive datetimes mixed with aware ones.
- Expecting `onupdate` to fire when only a child row changes.
- A constructor that takes a dependency and forgets `self.x = x`.
- Trusting incoming ids without a lookup, or relying on SQLite with foreign keys switched off.
- Doing the expiry check in Python, outside the transaction that claims the seat.

## Suggested Extension

Add a `login` method that returns a signed session token, rate-limits failed attempts per email with exponential lockout, and upgrades old hashes with `needs_rehash` on success. Then write a test that proves the failure path takes roughly the same time for unknown emails as for known ones (hash a dummy value) to avoid account enumeration by timing.
