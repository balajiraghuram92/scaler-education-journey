from datetime import datetime

import pytest
from freezegun import freeze_time

from library import Library
from models import Book, TimestampedMixin


def test_mixin_stamps_creation_time():
    with freeze_time("2026-03-04 05:06:07"):
        book = Book("ISBN-101", "Python Basics")
    assert book.created_at == datetime(2026, 3, 4, 5, 6, 7), "created_at must come from datetime.now()"
    assert isinstance(book, TimestampedMixin)


def test_mixin_forwards_arguments_to_the_next_class():
    class Base:
        def __init__(self, x, *, y=0):
            self.x, self.y = x, y

    class Stamped(TimestampedMixin, Base):
        pass

    obj = Stamped(5, y=6)
    assert (obj.x, obj.y) == (5, 6), "the mixin must forward *args and **kwargs with super().__init__"
    assert isinstance(obj.created_at, datetime)


def test_book_stores_fields_and_isbn_is_read_only():
    book = Book("ISBN-101", "Python Basics")
    assert (book.isbn, book.title) == ("ISBN-101", "Python Basics")
    with pytest.raises(AttributeError):
        book.isbn = "ISBN-999"
    book.title = "Renamed"
    assert book.title == "Renamed", "title stays a plain attribute"


def test_book_equality_and_hash_use_the_isbn():
    a, b = Book("ISBN-101", "A"), Book("ISBN-101", "B")
    assert a == b and hash(a) == hash(b), "same ISBN means equal, whatever the title"
    assert a != Book("ISBN-102", "A")
    assert len({a, b, Book("ISBN-102", "C")}) == 2, "books with the same ISBN collapse in a set"


def test_book_equality_with_foreign_types():
    book = Book("ISBN-101", "A")
    assert (book == "ISBN-101") is False
    assert book.__eq__("ISBN-101") is NotImplemented, "__eq__ must return NotImplemented for non-books"


def test_book_repr():
    assert repr(Book("ISBN-101", "Python Basics")) == "Book('ISBN-101', 'Python Basics')"


def make_library():
    lib = Library()
    lib.add_book(Book("ISBN-101", "Python Basics"))
    lib.add_book(Book("ISBN-102", "Advanced Python"))
    return lib


def test_library_len_and_repeatable_iteration():
    lib = make_library()
    assert len(lib) == 2 and len(Library()) == 0
    assert [b.isbn for b in lib] == ["ISBN-101", "ISBN-102"]
    assert [b.isbn for b in lib] == ["ISBN-101", "ISBN-102"], "iterating twice must work"


def test_library_membership_is_by_isbn_string():
    lib = make_library()
    assert "ISBN-101" in lib
    assert "ISBN-999" not in lib
    assert "Python Basics" not in lib, "titles are not ISBNs"


def test_library_indexing_and_slicing():
    lib = make_library()
    assert lib[0] == Book("ISBN-101", "x") and lib[-1].isbn == "ISBN-102"
    assert [b.isbn for b in lib[:]] == ["ISBN-101", "ISBN-102"]
    assert [b.isbn for b in lib[1:]] == ["ISBN-102"]
    with pytest.raises(IndexError):
        lib[2]
    assert repr(lib[0]) == "Book('ISBN-101', 'Python Basics')"
