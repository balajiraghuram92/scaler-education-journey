from .base_model import BaseModel


class Customer(BaseModel):
    def __init__(self, name=None):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
