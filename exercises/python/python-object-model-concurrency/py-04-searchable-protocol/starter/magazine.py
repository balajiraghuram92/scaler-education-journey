class Magazine:
    """A searchable item that can NOT be borrowed (it must not inherit from ``Borrowable``).

    - ``Magazine(title, issue)`` stores both and sets ``is_available = True``
    - ``matches(query)`` is true when ``query`` is contained in the title, case-insensitively
    """

    def __init__(self, title, issue):
        raise NotImplementedError("Implement Magazine.__init__")

    def matches(self, query: str) -> bool:
        raise NotImplementedError("Implement Magazine.matches")
