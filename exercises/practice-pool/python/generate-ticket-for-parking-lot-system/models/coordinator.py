from .base_model import BaseModel


class Coordinator(BaseModel):
    name: str
    email: str

    def __init__(self, name: str, email: str, id: int = None):
        super().__init__(id)
        self.name = name
        self.email = email

