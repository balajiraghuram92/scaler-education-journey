class LibraryError(Exception):
    """Base class so the controller can catch every domain failure in one clause."""


class MemberNotFoundError(LibraryError):
    pass


class BookNotFoundError(LibraryError):
    pass


class NoCopiesAvailableError(LibraryError):
    pass


class LoanLimitExceededError(LibraryError):
    pass
