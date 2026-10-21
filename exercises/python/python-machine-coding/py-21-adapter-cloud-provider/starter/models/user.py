from models.base_model import BaseModel

class User(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.password: str = ""
