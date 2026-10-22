from typing import Optional


class BaseModel:
    def __init__(self, id: Optional[int] = None):
        self.id = id
