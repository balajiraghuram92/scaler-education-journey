import pytest

from library import Book, Borrowable, Library, Member
from magazine import Magazine
from protocols import Searchable


def test_searchable_protocol_is_runtime_checkable():
    assert isinstance(Magazine("M", "1"), Searchable), "Searchable must be @runtime_checkable and Magazine must satisfy it"
    assert isinstance(Book("T", "A"), Searchable)
    assert not isinstance(object(), Searchable), "an object without matches() is not Searchable"


def test_magazine_is_searchable_but_not_borrowable():
    mag = Magazine("Python Monthly", "July 2026")
    assert (mag.title, mag.issue, mag.is_available) == ("Python Monthly", "July 2026", True)
    assert isinstance(mag, Searchable) and not isinstance(mag, Borrowable), "structural yes, nominal no"
    assert Borrowable not in type(mag).__mro__, "Magazine must not inherit from Borrowable"


def test_magazine_matches_title_case_insensitively():
    mag = Magazine("Python Monthly", "July 2026")
    assert mag.matches("python") and mag.matches("MONTHLY") and mag.matches("on mon")
    assert not mag.matches("java")
    assert not mag.matches("July"), "the issue is not searched"


def test_book_matches_title_or_author_case_insensitively():
    book = Book("Python Programming", "Guido")
    assert book.matches("python") and book.matches("GUIDO") and book.matches("gram")
    assert not book.matches("rossum")
    assert (book.title, book.author, book.is_available) == ("Python Programming", "Guido", True)


def test_borrowable_is_abstract_and_book_implements_it():
    with pytest.raises(TypeError):
        Borrowable()

    class Broken(Borrowable):
        pass

    with pytest.raises(TypeError):
        Broken()
    assert isinstance(Book("T", "A"), Borrowable)


def test_search_returns_matching_items_across_types():
    lib = Library()
    book, mag, other = Book("Python Programming", "Guido"), Magazine("Python Monthly", "July 2026"), Book("Cooking", "Sam")
    for item in (book, mag, other):
        lib.add_item(item)
    result = lib.search("python")
    assert result == [book, mag], "search returns matching books and magazines in insertion order"
    assert lib.search("sam") == [other]
    assert lib.search("zzz") == []
    assert Library().search("python") == []


def test_search_skips_items_that_are_not_searchable():
    class Poster:
        title = "python poster"

    lib = Library()
    lib.add_item(Poster())
    lib.add_item(Magazine("Python Monthly", "1"))
    assert len(lib.catalog) == 2, "add_item stores any item"
    assert len(lib.search("python")) == 1, "only Searchable items can match"


def test_lend_marks_a_book_unavailable():
    lib, book = Library(), Book("Python Programming", "Guido")
    lib.add_item(book)
    lib.lend(Member("Alice"), book)
    assert book.is_available is False


def test_lend_rejects_non_borrowable_items_without_side_effects():
    lib, mag = Library(), Magazine("Python Monthly", "July 2026")
    lib.add_item(mag)
    with pytest.raises(TypeError):
        lib.lend(Member("Alice"), mag)
    assert mag.is_available is True, "a refused lend must not change the item"
