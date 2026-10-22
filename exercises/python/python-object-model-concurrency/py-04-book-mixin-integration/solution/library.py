class Library:
    def __init__(self):
        self._books = []

    def add_book(self, book):
        self._books.append(book)

    def __len__(self):
        return len(self._books)

    def __iter__(self):
        return iter(self._books)

    def __contains__(self, isbn):
        return any(book.isbn == isbn for book in self._books)

    def __getitem__(self, index):
        return self._books[index]
