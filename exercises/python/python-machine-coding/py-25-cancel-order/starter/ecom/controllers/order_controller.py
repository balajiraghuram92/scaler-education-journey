from ecom.dtos import CancelOrderReqDto, CancelOrderResDto, ResponseStatus
from ecom.services.order_service import OrderService

class OrderController:

    def __init__(self, order_service: OrderService) -> None:
        """Keep the order service."""
        raise NotImplementedError('TODO: implement __init__')

    def cancel_order(self, request_dto: CancelOrderReqDto) -> CancelOrderResDto:
        """CancelOrderResDto(order, SUCCESS) on success; any exception becomes CancelOrderResDto(response_status=FAILURE)."""
        raise NotImplementedError('TODO: implement cancel_order')
