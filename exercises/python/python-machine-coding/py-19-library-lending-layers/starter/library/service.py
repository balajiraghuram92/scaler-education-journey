from library.exceptions import (
    BookNotFoundError,
    LoanLimitExceededError,
    MemberNotFoundError,
    NoCopiesAvailableError,
)
from library.models import Loan
from library.repositories import BookRepository, LoanRepository, MemberRepository


class LibraryService:
    """Business rules only: plain values in, domain objects out, never a DTO."""

    def __init__(self, books: BookRepository, members: MemberRepository, loans: LoanRepository) -> None:
        raise NotImplementedError("keep the three repositories")

    def lend_book(self, member_id: int, isbn: str) -> Loan:
        """Lend one copy.

        Raise MemberNotFoundError, BookNotFoundError, NoCopiesAvailableError or
        LoanLimitExceededError. Validate everything first and mutate last: a failed call
        must leave copies and loans unchanged. On success decrement copies_available,
        save the book and return the recorded Loan.
        """
        raise NotImplementedError
