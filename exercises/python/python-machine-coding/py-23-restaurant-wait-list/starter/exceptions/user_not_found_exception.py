class UserNotFoundException(Exception):
    """
    Raised when a user_id is provided that does not exist in the database.

    Example:
        raise UserNotFoundException("User not found")
    """

    def __init__(self, message: str):
        super().__init__(message)
