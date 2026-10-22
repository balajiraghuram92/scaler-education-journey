from dtos.response_status import ResponseStatus


class AddUserToWaitListResponseDto:
    def __init__(self, response_status: ResponseStatus, position: int = 0):
        self.response_status = response_status
        self.position = position
