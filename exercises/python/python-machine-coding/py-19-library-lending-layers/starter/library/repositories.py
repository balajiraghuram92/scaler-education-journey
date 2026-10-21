from typing import Protocol

from library.models import Book, Loan, Member


class BookRepository(Protocol):
    def find_by_isbn(self, isbn: str) -> Book | None: ...
    def save(self, book: Book) -> Book: ...


class MemberRepository(Protocol):
    def find_by_id(self, member_id: int) -> Member | None: ...


class LoanRepository(Protocol):
    def add(self, loan: Loan) -> Loan: ...
    def count_for_member(self, member_id: int) -> int: ...


class InMemoryBookRepository:
    """Dict-backed BookRepository keyed by ISBN. The constructor takes an optional list of books."""

    def __init__(self, books: list[Book] | None = None) -> None:
        raise NotImplementedError("store the books in a dict keyed by isbn")

    def find_by_isbn(self, isbn: str) -> Book | None:
        """Return the book or None."""
        raise NotImplementedError

    def save(self, book: Book) -> Book:
        """Insert or replace the book under its isbn and return it."""
        raise NotImplementedError


class InMemoryMemberRepository:
    """Dict-backed MemberRepository keyed by member id. The constructor takes an optional list of members."""

    def __init__(self, members: list[Member] | None = None) -> None:
        raise NotImplementedError("store the members in a dict keyed by id")

    def find_by_id(self, member_id: int) -> Member | None:
        """Return the member or None."""
        raise NotImplementedError


class InMemoryLoanRepository:
    """List-backed LoanRepository."""

    def __init__(self) -> None:
        raise NotImplementedError("start with no loans")

    def add(self, loan: Loan) -> Loan:
        """Record the loan and return it."""
        raise NotImplementedError

    def count_for_member(self, member_id: int) -> int:
        """Number of loans recorded for this member."""
        raise NotImplementedError
