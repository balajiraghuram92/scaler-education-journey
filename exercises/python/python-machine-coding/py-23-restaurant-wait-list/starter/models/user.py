from models.base_model import BaseModel
from models.user_type import UserType


class User(BaseModel):
    """
    Represents a person registered with the restaurant system.
    A user can be a regular customer (USER) or a restaurant admin (ADMIN).
    Only registered users can be added to the wait list.
    """

    def __init__(self, name: str, user_type: UserType):
        super().__init__()
        self.name = name
        self.user_type = user_type
