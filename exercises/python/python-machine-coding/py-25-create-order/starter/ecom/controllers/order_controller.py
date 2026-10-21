from ecom.dtos import PlaceOrderReqDto, PlaceOrderResDto, ResponseStatus
from ecom.services.order_service import OrderService

class OrderController:

    def __init__(self, order_service: OrderService) -> None:
        """Keep the order service."""
        raise NotImplementedError('TODO: implement __init__')

    def place_order(self, request_dto: PlaceOrderReqDto) -> PlaceOrderResDto:
        """PlaceOrderResDto(order, SUCCESS) on success; any exception becomes PlaceOrderResDto(response_status=FAILURE)."""
        raise NotImplementedError('TODO: implement place_order')
