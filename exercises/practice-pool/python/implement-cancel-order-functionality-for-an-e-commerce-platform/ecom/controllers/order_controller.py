from ecom.services import OrderService
from ecom.dtos import CancelOrderReqDto, CancelOrderResDto,  ResponseStatus
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

    def cancel_order(
            self,
            request_dto: CancelOrderReqDto
    ):
        try:
            order = self.order_service.cancel_order(
                request_dto.user_id,
                request_dto.order_id
            )

            response = CancelOrderResDto(
                response_status=ResponseStatus.SUCCESS,
                order=order
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = CancelOrderResDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
