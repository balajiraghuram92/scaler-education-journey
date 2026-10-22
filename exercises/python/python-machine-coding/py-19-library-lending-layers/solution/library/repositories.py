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
    def __init__(self, books: list[Book] | None = None) -> None:
        self._books = {b.isbn: b for b in books or []}

    def find_by_isbn(self, isbn: str) -> Book | None:
        return self._books.get(isbn)

    def save(self, book: Book) -> Book:
        self._books[book.isbn] = book
        return book


class InMemoryMemberRepository:
    def __init__(self, members: list[Member] | None = None) -> None:
        self._members = {m.id: m for m in members or []}

    def find_by_id(self, member_id: int) -> Member | None:
        return self._members.get(member_id)


class InMemoryLoanRepository:
    def __init__(self) -> None:
        self._loans: list[Loan] = []

    def add(self, loan: Loan) -> Loan:
        self._loans.append(loan)
        return loan

    def count_for_member(self, member_id: int) -> int:
        return sum(1 for loan in self._loans if loan.member_id == member_id)
