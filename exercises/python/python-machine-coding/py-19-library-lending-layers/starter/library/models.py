from dataclasses import dataclass


@dataclass
class Book:
    isbn: str
    title: str
    copies_available: int


@dataclass
class Member:
    id: int
    name: str
    max_loans: int = 3


@dataclass(frozen=True)
class Loan:
    member_id: int
    isbn: str
