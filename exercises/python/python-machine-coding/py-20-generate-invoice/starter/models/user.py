from models.base_model import BaseModel
from models.user_type import UserType

class User(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.password: str = ""
        self.phone: str = ""
        self.user_type: UserType = None
