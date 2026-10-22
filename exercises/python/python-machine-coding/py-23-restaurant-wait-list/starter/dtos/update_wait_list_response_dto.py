from dtos.response_status import ResponseStatus


class UpdateWaitListResponseDto:
    def __init__(self, response_status: ResponseStatus):
        self.response_status = response_status
