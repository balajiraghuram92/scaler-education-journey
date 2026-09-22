from ecom.services import ProductService
from ecom.dtos import DeliveryEstimateReqDto, DeliveryEstimateResDto, ResponseStatus
from logging import getLogger, DEBUG
import traceback


class ProductController:
    product_service: ProductService

    def __init__(
            self,
            product_service: ProductService
    ):
        self.product_service = product_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def get_estimated_delivery(
            self,
            request_dto: DeliveryEstimateReqDto
    ):
        try:
            expected_delivery = self.product_service.estimate_delivery_date(
                request_dto.product_id,
                request_dto.address_id
            )

            response = DeliveryEstimateResDto(
                response_status=ResponseStatus.SUCCESS,
                expected_delivery=expected_delivery
            )

        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = DeliveryEstimateResDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
