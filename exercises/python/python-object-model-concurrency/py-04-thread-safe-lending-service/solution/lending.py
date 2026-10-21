import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta


class LibraryError(Exception):
    """Base class for business-rule failures."""


class UnknownItem(LibraryError):
    pass


class NoCopiesAvailable(LibraryError):
    pass


class BorrowLimitReached(LibraryError):
    pass


class NotBorrowedByMember(LibraryError):
    pass


@dataclass(frozen=True)
class Loan:
    member_id: str
    isbn: str
    due: datetime


class LendingService:
    LOAN_DAYS = 14

    def __init__(
        self,
        copies: Mapping[str, int],
        *,
        max_loans: int = 5,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        if max_loans < 1:
            raise ValueError("max_loans must be >= 1")
        self._available = dict(copies)
        self._max_loans = max_loans
        self._clock = clock
        self._loans: dict[str, list[Loan]] = {}
        self._lock = threading.Lock()

    def lend(self, member_id: str, isbn: str) -> Loan:
        with self._lock:                                   # check and update as one step
            if isbn not in self._available:
                raise UnknownItem(isbn)
            if self._available[isbn] < 1:
                raise NoCopiesAvailable(isbn)
            if len(self._loans.get(member_id, [])) >= self._max_loans:
                raise BorrowLimitReached(member_id)
            loan = Loan(member_id, isbn, self._clock() + timedelta(days=self.LOAN_DAYS))
            self._available[isbn] -= 1
            self._loans.setdefault(member_id, []).append(loan)
            return loan

    def return_book(self, member_id: str, isbn: str) -> None:
        with self._lock:
            active = self._loans.get(member_id, [])
            for i, loan in enumerate(active):
                if loan.isbn == isbn:
                    del active[i]
                    self._available[isbn] += 1
                    return
            raise NotBorrowedByMember(f"{member_id} has not borrowed {isbn}")

    def available(self, isbn: str) -> int:
        with self._lock:
            return self._available[isbn]

    def active_loans(self, member_id: str) -> list[Loan]:
        with self._lock:
            return list(self._loans.get(member_id, []))
