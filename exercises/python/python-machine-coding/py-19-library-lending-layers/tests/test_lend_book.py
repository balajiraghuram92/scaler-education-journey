import pytest

from library.controller import LendBookRequest, LibraryController, ResponseStatus
from library.exceptions import (
    BookNotFoundError,
    LibraryError,
    LoanLimitExceededError,
    MemberNotFoundError,
    NoCopiesAvailableError,
)
from library.models import Book, Loan, Member
from library.repositories import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryMemberRepository,
)
from library.service import LibraryService


def make(books, members):
    book_repo = InMemoryBookRepository(books)
    loan_repo = InMemoryLoanRepository()
    service = LibraryService(book_repo, InMemoryMemberRepository(members), loan_repo)
    return service, LibraryController(service), book_repo, loan_repo


def test_successful_loan_decrements_copies_and_records_loan():
    service, controller, books, loans = make([Book("111", "SICP", 2)], [Member(1, "Asha")])
    response = controller.lend_book(LendBookRequest(1, "111"))
    assert response.status is ResponseStatus.SUCCESS
    assert books.find_by_isbn("111").copies_available == 1, "one copy should have been taken"
    assert loans.count_for_member(1) == 1


def test_service_returns_the_loan():
    service, _, _, _ = make([Book("111", "SICP", 1)], [Member(1, "Asha")])
    loan = service.lend_book(1, "111")
    assert loan == Loan(1, "111")


def test_unknown_member_raises():
    service, _, books, loans = make([Book("111", "SICP", 1)], [Member(1, "Asha")])
    with pytest.raises(MemberNotFoundError):
        service.lend_book(9, "111")
    assert books.find_by_isbn("111").copies_available == 1
    assert loans.count_for_member(9) == 0


def test_unknown_book_raises():
    service, _, _, loans = make([Book("111", "SICP", 1)], [Member(1, "Asha")])
    with pytest.raises(BookNotFoundError):
        service.lend_book(1, "nope")
    assert loans.count_for_member(1) == 0


def test_no_copies_left_raises():
    service, _, _, loans = make([Book("111", "SICP", 0)], [Member(1, "Asha")])
    with pytest.raises(NoCopiesAvailableError):
        service.lend_book(1, "111")
    assert loans.count_for_member(1) == 0


def test_loan_limit_enforced_and_failed_call_leaves_state_unchanged():
    books = [Book(str(i), f"B{i}", 5) for i in range(4)]
    service, controller, repo, loans = make(books, [Member(1, "Asha", max_loans=3)])
    for i in range(3):
        service.lend_book(1, str(i))
    with pytest.raises(LoanLimitExceededError):
        service.lend_book(1, "3")
    assert repo.find_by_isbn("3").copies_available == 5, "validate first, mutate last"
    assert loans.count_for_member(1) == 3
    response = controller.lend_book(LendBookRequest(1, "3"))
    assert response.status is ResponseStatus.FAILURE
    assert "loan limit" in response.message


def test_custom_max_loans_is_respected():
    books = [Book("a", "A", 3), Book("b", "B", 3)]
    service, _, _, _ = make(books, [Member(1, "Asha", max_loans=1)])
    service.lend_book(1, "a")
    with pytest.raises(LoanLimitExceededError):
        service.lend_book(1, "b")


def test_controller_wraps_failure_with_message():
    _, controller, books, _ = make([Book("111", "SICP", 1)], [Member(1, "Asha")])
    response = controller.lend_book(LendBookRequest(9, "111"))
    assert response.status is ResponseStatus.FAILURE
    assert response.message, "failure responses must carry the exception message"
    assert books.find_by_isbn("111").copies_available == 1


def test_controller_only_catches_library_errors():
    class Broken:
        def lend_book(self, member_id, isbn):
            raise RuntimeError("bug")

    controller = LibraryController(Broken())
    with pytest.raises(RuntimeError):
        controller.lend_book(LendBookRequest(1, "x"))


def test_exception_hierarchy_and_immutable_loan():
    for exc in (MemberNotFoundError, BookNotFoundError, NoCopiesAvailableError, LoanLimitExceededError):
        assert issubclass(exc, LibraryError)
    loan = Loan(1, "x")
    with pytest.raises(Exception):
        loan.member_id = 2
