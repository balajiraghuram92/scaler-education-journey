class UnauthorizedAccessException(Exception):
    """
    Raised when a non-admin user tries to perform an admin-only action
    (such as removing customers from the wait list).

    Example:
        raise UnauthorizedAccessException("Access Denied")
    """

    def __init__(self, message: str):
        super().__init__(message)
