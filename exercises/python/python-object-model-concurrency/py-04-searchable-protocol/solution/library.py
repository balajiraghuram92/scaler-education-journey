from abc import ABC, abstractmethod

from protocols import Searchable


class Borrowable(ABC):
    @abstractmethod
    def borrow(self):
        pass


class Book(Borrowable):
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.is_available = True

    def matches(self, query: str) -> bool:
        query = query.lower()
        return query in self.title.lower() or query in self.author.lower()

    def borrow(self):
        return self.title


class Member:
    def __init__(self, name):
        self.name = name


class Library:
    def __init__(self):
        self.catalog = []

    def add_item(self, item):
        self.catalog.append(item)

    def search(self, query):
        return [
            item
            for item in self.catalog
            if isinstance(item, Searchable) and item.matches(query)
        ]

    def lend(self, member, item):
        if not isinstance(item, Borrowable):
            raise TypeError("Item is not borrowable")

        item.is_available = False
