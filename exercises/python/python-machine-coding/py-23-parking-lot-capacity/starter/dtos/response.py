from dtos.response_status import ResponseStatus

class Response:
    def __init__(self, response_status: ResponseStatus, message: str):
        self.response_status = response_status
        self.message = message
