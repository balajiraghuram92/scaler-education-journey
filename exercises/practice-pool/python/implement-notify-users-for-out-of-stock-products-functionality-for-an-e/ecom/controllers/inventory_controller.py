from ecom.services import InventoryService
from ecom.dtos import CreateUpdateInventoryReqDto, CreateUpdateInventoryResDto, ResponseStatus

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
            inventory = self.inventory_service.save_or_update_inventory(
                request_dto.product_id,
                request_dto.quantity
            )

            response = CreateUpdateInventoryResDto(
                response_status=ResponseStatus.SUCCESS,
                inventory=inventory
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = CreateUpdateInventoryResDto(
                response_status=ResponseStatus.FAILURE
            )

        return response