from datetime import datetime


class TimestampedMixin:
    def __init__(self, *args, **kwargs):
        self.created_at = datetime.now()
        super().__init__(*args, **kwargs)


class Book(TimestampedMixin):
    def __init__(self, isbn, title):
        super().__init__()
        self._isbn = isbn
        self.title = title

    @property
    def isbn(self):
        return self._isbn

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.isbn == other.isbn

    def __hash__(self):
        return hash(self.isbn)

    def __repr__(self):
        return f"Book('{self.isbn}', '{self.title}')"
