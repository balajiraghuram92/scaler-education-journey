from models.base_model import BaseModel
from models.symbol import Symbol

class Player(BaseModel):
    def __init__(self, name: str, symbol: Symbol):
        super().__init__()
        self.name = name
        self.symbol = symbol
