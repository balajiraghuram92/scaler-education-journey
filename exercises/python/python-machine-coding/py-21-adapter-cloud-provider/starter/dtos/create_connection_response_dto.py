from models.enums import ConnectionStatus, ResponseStatus
from typing import Optional

class CreateConnectionResponseDto:
    def __init__(self):
        self.connection_id: Optional[str] = None
        self.response_status: ResponseStatus = ResponseStatus.FAILURE
        self.connection_status: Optional[ConnectionStatus] = None
