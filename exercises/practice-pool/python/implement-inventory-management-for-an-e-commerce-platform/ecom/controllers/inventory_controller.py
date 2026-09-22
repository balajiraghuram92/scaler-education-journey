from ecom.services import InventoryService
from ecom.dtos import CreateUpdateInventoryReqDto, CreateUpdateInventoryResponseDto, ResponseStatus
from ecom.dtos import DeleteInventoryReqDto, DeleteInventoryResponseDto
from logging import getLogger, DEBUG
import traceback


class InventoryController:
    inventory_service: InventoryService

    def __init__(
            self,
            inventory_service: InventoryService
    ):
        self.inventory_service = inventory_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def create_or_update_inventory(
            self,
            request_dto: CreateUpdateInventoryReqDto
    ):
        try:
            inventory = self.inventory_service.create_or_update_inventory(
                request_dto.user_id,
                request_dto.product_id,
                request_dto.quantity
            )

            response = CreateUpdateInventoryResponseDto(
                response_status=ResponseStatus.SUCCESS,
                inventory=inventory
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = CreateUpdateInventoryResponseDto(
                response_status=ResponseStatus.FAILURE
            )

        return response

    def delete_inventory(
            self,
            request_dto: DeleteInventoryReqDto
    ):
        try:
            self.inventory_service.delete_inventory(
                request_dto.user_id,
                request_dto.product_id
            )

            response = DeleteInventoryResponseDto(
                response_status=ResponseStatus.SUCCESS
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = DeleteInventoryResponseDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
