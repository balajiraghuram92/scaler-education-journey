from ecom.dtos import CreateUpdateInventoryReqDto, CreateUpdateInventoryResDto, ResponseStatus
from ecom.services.inventory_service import InventoryService


class InventoryController:
    def __init__(self, inventory_service: InventoryService) -> None:
        self.inventory_service = inventory_service

    def create_or_update_inventory(self, request_dto: CreateUpdateInventoryReqDto) -> CreateUpdateInventoryResDto:
        try:
            inventory = self.inventory_service.save_or_update_inventory(request_dto.product_id, request_dto.quantity)
            return CreateUpdateInventoryResDto(response_status=ResponseStatus.SUCCESS, inventory=inventory)
        except Exception:
            return CreateUpdateInventoryResDto(response_status=ResponseStatus.FAILURE)
