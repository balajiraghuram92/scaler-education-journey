from ecom.dtos import CancelOrderReqDto, CancelOrderResDto, ResponseStatus
from ecom.services.order_service import OrderService


class OrderController:
    def __init__(self, order_service: OrderService) -> None:
        self.order_service = order_service

    def cancel_order(self, request_dto: CancelOrderReqDto) -> CancelOrderResDto:
        try:
            order = self.order_service.cancel_order(request_dto.user_id, request_dto.order_id)
            return CancelOrderResDto(order=order, response_status=ResponseStatus.SUCCESS)
        except Exception:
            return CancelOrderResDto(response_status=ResponseStatus.FAILURE)
