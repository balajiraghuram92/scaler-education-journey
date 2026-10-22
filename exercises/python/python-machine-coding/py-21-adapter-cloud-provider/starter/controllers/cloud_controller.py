from dtos.create_connection_request_dto import CreateConnectionRequestDto
from dtos.create_connection_response_dto import CreateConnectionResponseDto
from dtos.create_connection_response_dto import ResponseStatus
from exceptions.exceptions import UserNotFoundException
from services.cloud_service import CloudService

class CloudController:

    def __init__(self, cloud_service: CloudService):
        """Keep the service."""
        raise NotImplementedError('TODO: implement __init__')

    def create_connection(self, request: CreateConnectionRequestDto) -> CreateConnectionResponseDto:
        """On success fill connection_id, connection_status and ResponseStatus.SUCCESS on the response DTO. UserNotFoundException becomes ResponseStatus.FAILURE; other errors propagate."""
        raise NotImplementedError('TODO: implement create_connection')
