from ecom.services import OrderService
from ecom.dtos import PlaceOrderReqDto, PlaceOrderResDto,  ResponseStatus
from logging import getLogger, DEBUG
import traceback


class OrderController:
    order_service: OrderService

    def __init__(
            self,
            order_service: OrderService
    ):
        self.order_service = order_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def place_order(
            self,
            request_dto: PlaceOrderReqDto
    ):
        try:
            order = self.order_service.place_order(
                request_dto.user_id,
                request_dto.product_ids_with_quantity
            )

            response = PlaceOrderResDto(
                response_status=ResponseStatus.SUCCESS,
                order=order
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = PlaceOrderResDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
