from datetime import datetime  # noqa: F401


class TimestampedMixin:
    """``__init__(*args, **kwargs)`` sets ``self.created_at = datetime.now()`` and then continues
    the cooperative chain with ``super().__init__(*args, **kwargs)``."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Implement TimestampedMixin.__init__")


class Book(TimestampedMixin):
    """``Book(isbn, title)``: value object identified by its ISBN.

    - ``isbn`` is a read-only property (assignment raises ``AttributeError``)
    - ``__eq__`` compares ISBNs and returns ``NotImplemented`` for non-books
    - ``__hash__`` is ``hash(isbn)``
    - ``__repr__`` is ``Book('<isbn>', '<title>')``
    """

    def __init__(self, isbn, title):
        raise NotImplementedError("Implement Book.__init__")

    @property
    def isbn(self):
        raise NotImplementedError("Implement Book.isbn")

    def __eq__(self, other):
        raise NotImplementedError("Implement Book.__eq__")

    def __hash__(self):
        raise NotImplementedError("Implement Book.__hash__")

    def __repr__(self):
        raise NotImplementedError("Implement Book.__repr__")
