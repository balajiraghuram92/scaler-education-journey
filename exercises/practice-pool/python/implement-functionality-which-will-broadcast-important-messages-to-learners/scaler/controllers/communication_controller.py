from typing import List

from scaler.models import Communication
from scaler.services import CommunicationService
from scaler.dtos import BroadcastMessageReqDto, BroadcastMessageResDto
from scaler.dtos import ResponseStatus


class CommunicationController:
    communication_service: CommunicationService

    def __init__(
            self,
            communication_service: CommunicationService
    ):
        self.communication_service = communication_service

    def broadcast_message(
            self,
            request_dto: BroadcastMessageReqDto
    ):

        try:
            response: Communication= self.communication_service.broadcast_message(
                batch_id=request_dto.batch_id,
                sender_id=request_dto.sender_id,
                message=request_dto.message
            )

            response_dto = BroadcastMessageResDto(
                communication=response,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            response_dto = BroadcastMessageResDto(
                communication=None,
                response_status=ResponseStatus.FAILURE
            )

        return response_dto


