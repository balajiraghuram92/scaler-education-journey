class InvalidGateException(Exception):
    """
    Raised when a gate ID is invalid, does not exist, or is an exit gate.
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
