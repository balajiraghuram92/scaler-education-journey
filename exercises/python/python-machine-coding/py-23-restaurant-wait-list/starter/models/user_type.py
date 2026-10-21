from enum import Enum


class UserType(Enum):
    """
    Distinguishes the role of a user in the system.
    ADMIN -> a restaurant staff member who manages the wait list
    USER  -> a regular customer who can add themselves to the wait list
    """
    ADMIN = "ADMIN"
    USER = "USER"
