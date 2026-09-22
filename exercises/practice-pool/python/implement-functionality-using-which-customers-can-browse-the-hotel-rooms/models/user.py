from .base_model import BaseModel


class User(BaseModel):
    name: str
    password: str
    phone: str

    def __init__(self, name=None, password=None, phone=None):
        super().__init__()
        self.name = name
        self.password = password
        self.phone = phone
