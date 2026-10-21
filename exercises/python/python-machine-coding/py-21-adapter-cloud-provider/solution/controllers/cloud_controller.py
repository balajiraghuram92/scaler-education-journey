from dtos.create_connection_request_dto import CreateConnectionRequestDto
from dtos.create_connection_response_dto import CreateConnectionResponseDto
from dtos.create_connection_response_dto import ResponseStatus
from exceptions.exceptions import UserNotFoundException
from services.cloud_service import CloudService

class CloudController:
    def __init__(self, cloud_service: CloudService):
        self.cloud_service = cloud_service

    def create_connection(self, request: CreateConnectionRequestDto) -> CreateConnectionResponseDto:
        response = CreateConnectionResponseDto()
        try:
            connection = self.cloud_service.create_connection(request.user_id)
            response.connection_id = connection.connection_id
            response.connection_status = connection.connection_status
            response.response_status = ResponseStatus.SUCCESS
        except UserNotFoundException:
            response.response_status = ResponseStatus.FAILURE
        return response
