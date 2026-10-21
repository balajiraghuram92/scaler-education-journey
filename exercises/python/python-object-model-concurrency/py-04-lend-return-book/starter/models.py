from abc import ABC, abstractmethod


class User:
    def __init__(self, name):
        self.name = name


class Member(User):
    def __init__(self, name, borrow_limit=3):
        super().__init__(name)
        self.borrow_limit = borrow_limit
        self.borrowed = 0

    def can_borrow(self):
        return self.borrowed < self.borrow_limit

    def increment_borrow(self):
        self.borrowed += 1

    def decrement_borrow(self):
        if self.borrowed > 0:
            self.borrowed -= 1


class Borrowable(ABC):
    @abstractmethod
    def borrow(self):
        pass


class Book(Borrowable):
    def __init__(self, title):
        self.title = title
        self.is_available = True

    def borrow(self):
        return self.title


class Novel(Book):
    pass


class Loan:
    def __init__(self, member, book):
        self.member = member
        self.book = book
