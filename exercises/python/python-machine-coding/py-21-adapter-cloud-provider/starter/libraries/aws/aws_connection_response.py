import datetime

class AWSConnectionResponse:
    def __init__(self):
        self.connection_id: str = ""
        self.connection_status: str = ""
        self.connection_date: datetime.datetime = datetime.datetime.now()
