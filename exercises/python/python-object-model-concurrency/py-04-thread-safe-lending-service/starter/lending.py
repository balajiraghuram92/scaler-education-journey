import threading  # noqa: F401
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta  # noqa: F401


class LibraryError(Exception):
    """Base class for every business-rule failure."""


class UnknownItem(LibraryError):
    """The ISBN is not in the catalog."""


class NoCopiesAvailable(LibraryError):
    """Every copy of the item is already lent."""


class BorrowLimitReached(LibraryError):
    """The member already has ``max_loans`` active loans."""


class NotBorrowedByMember(LibraryError):
    """The member is returning something they do not hold."""


@dataclass(frozen=True)
class Loan:
    member_id: str
    isbn: str
    due: datetime


class LendingService:
    """Thread-safe lending with an injectable clock.

    - ``LendingService(copies, *, max_loans=5, clock=datetime.now)``; ``max_loans < 1`` raises ``ValueError``;
      copy the ``copies`` mapping instead of sharing it
    - ``lend(member_id, isbn) -> Loan`` checks in this order: unknown ISBN (``UnknownItem``),
      no copies (``NoCopiesAvailable``), member limit (``BorrowLimitReached``). On success it decrements
      the available count, records the loan and returns it with ``due = clock() + 14 days``.
      A failed call must change no state.
    - ``return_book(member_id, isbn)`` removes that member's loan and restores the copy, or raises
      ``NotBorrowedByMember``
    - ``available(isbn)`` and ``active_loans(member_id)`` return consistent snapshots (the latter a NEW list)
    - one ``threading.Lock`` makes every check-and-update atomic
    """

    LOAN_DAYS = 14

    def __init__(
        self,
        copies: Mapping[str, int],
        *,
        max_loans: int = 5,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        raise NotImplementedError("Implement LendingService.__init__")

    def lend(self, member_id: str, isbn: str) -> Loan:
        raise NotImplementedError("Implement LendingService.lend")

    def return_book(self, member_id: str, isbn: str) -> None:
        raise NotImplementedError("Implement LendingService.return_book")

    def available(self, isbn: str) -> int:
        raise NotImplementedError("Implement LendingService.available")

    def active_loans(self, member_id: str) -> list[Loan]:
        raise NotImplementedError("Implement LendingService.active_loans")
