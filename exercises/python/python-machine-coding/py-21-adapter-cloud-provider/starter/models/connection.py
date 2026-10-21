from models.base_model import BaseModel
from models.enums import ConnectionStatus

class Connection(BaseModel):
    def __init__(self):
        super().__init__()
        self.connection_id: str = ""
        self.connection_status: ConnectionStatus = ConnectionStatus.FAILURE
        self.user_id: int = 0
