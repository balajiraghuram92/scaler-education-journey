from abc import ABC, abstractmethod

from protocols import Searchable  # noqa: F401


class Borrowable(ABC):
    """Nominal contract for lendable items: abstract ``borrow()``."""

    @abstractmethod
    def borrow(self):
        pass


class Book(Borrowable):
    """``Book(title, author)`` is borrowable and searchable.

    - stores ``title``, ``author`` and ``is_available = True``
    - ``matches(query)``: case-insensitive match on the title or the author
    - implements ``borrow()`` (return the title)
    """

    def __init__(self, title, author):
        raise NotImplementedError("Implement Book.__init__")

    def matches(self, query: str) -> bool:
        raise NotImplementedError("Implement Book.matches")

    def borrow(self):
        raise NotImplementedError("Implement Book.borrow")


class Member:
    def __init__(self, name):
        self.name = name


class Library:
    """Catalog of any items.

    - ``add_item(item)`` stores any item
    - ``search(query)`` returns the items for which ``isinstance(item, Searchable)`` and ``item.matches(query)``
    - ``lend(member, item)`` raises ``TypeError`` when the item is not ``Borrowable``,
      otherwise marks it unavailable
    """

    def __init__(self):
        self.catalog = []

    def add_item(self, item):
        raise NotImplementedError("Implement Library.add_item")

    def search(self, query):
        raise NotImplementedError("Implement Library.search")

    def lend(self, member, item):
        raise NotImplementedError("Implement Library.lend")
