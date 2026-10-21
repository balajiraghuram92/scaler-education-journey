class Library:
    """A collection of books that behaves like a built-in container.

    - ``add_book(book)``
    - ``len(library)`` and iteration
    - ``isbn in library``: membership by ISBN string
    - ``library[0]`` and ``library[:]``: indexing and slicing (delegating to a list gives slices for free)
    """

    def __init__(self):
        raise NotImplementedError("Implement Library.__init__")

    def add_book(self, book):
        raise NotImplementedError("Implement Library.add_book")

    def __len__(self):
        raise NotImplementedError("Implement Library.__len__")

    def __iter__(self):
        raise NotImplementedError("Implement Library.__iter__")

    def __contains__(self, isbn):
        raise NotImplementedError("Implement Library.__contains__")

    def __getitem__(self, index):
        raise NotImplementedError("Implement Library.__getitem__")
