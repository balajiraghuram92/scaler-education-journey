from models import Borrowable, Loan  # noqa: F401


class Library:
    """Lending service built on the classes in ``models.py``."""

    def lend_book(self, member, book):
        """Lend ``book`` to ``member`` and return a ``Loan(member, book)``.

        Check the rules in this order, before changing anything:
        1. ``TypeError("Item is not borrowable")`` if ``book`` is not a ``Borrowable``
        2. ``ValueError("Book not available")`` if ``book.is_available`` is false
        3. ``ValueError("Borrow limit reached")`` if ``member.can_borrow()`` is false
        On success set ``book.is_available = False`` and call ``member.increment_borrow()``.
        """
        raise NotImplementedError("Implement Library.lend_book")

    def return_book(self, member, book):
        """Set ``book.is_available = True`` and call ``member.decrement_borrow()``."""
        raise NotImplementedError("Implement Library.return_book")
