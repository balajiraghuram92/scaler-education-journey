from ecom.dtos import PlaceOrderReqDto, PlaceOrderResDto, ResponseStatus
from ecom.services.order_service import OrderService


class OrderController:
    def __init__(self, order_service: OrderService) -> None:
        self.order_service = order_service

    def place_order(self, request_dto: PlaceOrderReqDto) -> PlaceOrderResDto:
        try:
            order = self.order_service.place_order(request_dto.user_id, request_dto.product_ids_with_quantity)
            return PlaceOrderResDto(order=order, response_status=ResponseStatus.SUCCESS)
        except Exception:
            return PlaceOrderResDto(response_status=ResponseStatus.FAILURE)
