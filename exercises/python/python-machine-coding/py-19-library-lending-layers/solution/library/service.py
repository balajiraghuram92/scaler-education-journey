from library.exceptions import (
    BookNotFoundError,
    LoanLimitExceededError,
    MemberNotFoundError,
    NoCopiesAvailableError,
)
from library.models import Loan
from library.repositories import BookRepository, LoanRepository, MemberRepository


class LibraryService:
    """Business rules only: plain values in, domain objects out, no DTOs."""

    def __init__(self, books: BookRepository, members: MemberRepository, loans: LoanRepository) -> None:
        self._books = books
        self._members = members
        self._loans = loans

    def lend_book(self, member_id: int, isbn: str) -> Loan:
        member = self._members.find_by_id(member_id)
        if member is None:
            raise MemberNotFoundError(f"member {member_id} not found")
        book = self._books.find_by_isbn(isbn)
        if book is None:
            raise BookNotFoundError(f"book {isbn} not found")
        if book.copies_available <= 0:
            raise NoCopiesAvailableError(f"no copies of {isbn} left")
        if self._loans.count_for_member(member_id) >= member.max_loans:
            raise LoanLimitExceededError(f"member {member_id} is at the loan limit")
        # every check passed: only now do we mutate state
        book.copies_available -= 1
        self._books.save(book)
        return self._loans.add(Loan(member_id, isbn))
