import pytest

from library import Library
from models import Book, Loan, Member, Novel


def test_successful_lend_returns_loan_and_updates_state():
    library, member, book = Library(), Member("Alice"), Novel("The Hobbit")
    loan = library.lend_book(member, book)
    assert isinstance(loan, Loan), "lend_book must return a Loan"
    assert loan.member is member and loan.book is book, "the Loan must reference the member and the book"
    assert book.is_available is False, "the lent book is no longer available"
    assert member.borrowed == 1, "the member's borrow count must go up"


def test_non_borrowable_item_is_rejected():
    class Poster:  # not a Borrowable, and has no is_available at all
        pass

    with pytest.raises(TypeError) as info:
        Library().lend_book(Member("Alice"), Poster())
    assert str(info.value) == "Item is not borrowable"


def test_unavailable_book_is_rejected():
    library, book = Library(), Book("Dune")
    library.lend_book(Member("Alice"), book)
    with pytest.raises(ValueError) as info:
        library.lend_book(Member("Bob"), book)
    assert str(info.value) == "Book not available"


def test_borrow_limit_is_enforced():
    library, member = Library(), Member("Alice", borrow_limit=2)
    library.lend_book(member, Book("A"))
    library.lend_book(member, Book("B"))
    with pytest.raises(ValueError) as info:
        library.lend_book(member, Book("C"))
    assert str(info.value) == "Borrow limit reached"


def test_rules_are_checked_in_the_documented_order():
    library = Library()
    full = Member("Full", borrow_limit=0)
    taken = Book("Taken")
    taken.is_available = False
    with pytest.raises(ValueError, match="Book not available"):
        library.lend_book(full, taken)  # availability is checked before the member limit
    with pytest.raises(TypeError):
        library.lend_book(full, object())  # type is checked before everything else


def test_failed_lend_changes_no_state():
    library, member, book = Library(), Member("Alice", borrow_limit=0), Book("Dune")
    with pytest.raises(ValueError):
        library.lend_book(member, book)
    assert book.is_available is True, "a refused lend must leave the book available"
    assert member.borrowed == 0, "a refused lend must not touch the member's count"


def test_return_restores_availability_and_count():
    library, member, book = Library(), Member("Alice"), Novel("The Hobbit")
    library.lend_book(member, book)
    library.return_book(member, book)
    assert book.is_available is True and member.borrowed == 0


def test_borrow_cycle_up_to_the_limit_and_again_after_a_return():
    library, member = Library(), Member("Alice", borrow_limit=3)
    books = [Book(f"B{i}") for i in range(4)]
    for b in books[:3]:
        library.lend_book(member, b)
    with pytest.raises(ValueError, match="Borrow limit reached"):
        library.lend_book(member, books[3])
    library.return_book(member, books[0])
    library.lend_book(member, books[3])  # a slot is free again
    assert member.borrowed == 3 and books[0].is_available and not books[3].is_available


def test_service_uses_the_member_methods():
    class SpyMember:
        def __init__(self):
            self.calls = []

        def can_borrow(self):
            self.calls.append("can_borrow")
            return True

        def increment_borrow(self):
            self.calls.append("increment")

        def decrement_borrow(self):
            self.calls.append("decrement")

    spy, book = SpyMember(), Book("X")
    library = Library()
    library.lend_book(spy, book)
    library.return_book(spy, book)
    assert spy.calls == ["can_borrow", "increment", "decrement"], (
        "use member.can_borrow(), member.increment_borrow() and member.decrement_borrow()"
    )
