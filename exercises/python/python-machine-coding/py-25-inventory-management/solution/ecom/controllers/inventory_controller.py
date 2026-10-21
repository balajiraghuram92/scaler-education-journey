from ecom.dtos import (
    CreateUpdateInventoryReqDto,
    CreateUpdateInventoryResponseDto,
    DeleteInventoryReqDto,
    DeleteInventoryResponseDto,
    ResponseStatus,
)
from ecom.services.inventory_service import InventoryService


class InventoryController:
    def __init__(self, inventory_service: InventoryService) -> None:
        self.inventory_service = inventory_service

    def create_or_update_inventory(self, request_dto: CreateUpdateInventoryReqDto) -> CreateUpdateInventoryResponseDto:
        try:
            inventory = self.inventory_service.create_or_update_inventory(
                request_dto.user_id, request_dto.product_id, request_dto.quantity)
            return CreateUpdateInventoryResponseDto(inventory=inventory, response_status=ResponseStatus.SUCCESS)
        except Exception:
            return CreateUpdateInventoryResponseDto(response_status=ResponseStatus.FAILURE)

    def delete_inventory(self, request_dto: DeleteInventoryReqDto) -> DeleteInventoryResponseDto:
        try:
            self.inventory_service.delete_inventory(request_dto.user_id, request_dto.product_id)
            return DeleteInventoryResponseDto(response_status=ResponseStatus.SUCCESS)
        except Exception:
            return DeleteInventoryResponseDto(response_status=ResponseStatus.FAILURE)
