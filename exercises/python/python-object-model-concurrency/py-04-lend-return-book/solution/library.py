from models import Borrowable, Loan


class Library:
    def lend_book(self, member, book):
        if not isinstance(book, Borrowable):
            raise TypeError("Item is not borrowable")

        if not book.is_available:
            raise ValueError("Book not available")

        if not member.can_borrow():
            raise ValueError("Borrow limit reached")

        book.is_available = False
        member.increment_borrow()

        return Loan(member, book)

    def return_book(self, member, book):
        book.is_available = True
        member.decrement_borrow()
