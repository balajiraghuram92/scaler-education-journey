from ecom.dtos import CreateUpdateInventoryReqDto, CreateUpdateInventoryResponseDto, DeleteInventoryReqDto, DeleteInventoryResponseDto, ResponseStatus
from ecom.services.inventory_service import InventoryService

class InventoryController:

    def __init__(self, inventory_service: InventoryService) -> None:
        """Keep the inventory service."""
        raise NotImplementedError('TODO: implement __init__')

    def create_or_update_inventory(self, request_dto: CreateUpdateInventoryReqDto) -> CreateUpdateInventoryResponseDto:
        """SUCCESS with the inventory, or FAILURE (inventory None) on any exception."""
        raise NotImplementedError('TODO: implement create_or_update_inventory')

    def delete_inventory(self, request_dto: DeleteInventoryReqDto) -> DeleteInventoryResponseDto:
        """SUCCESS, or FAILURE on any exception."""
        raise NotImplementedError('TODO: implement delete_inventory')
