from ecom.dtos import DeliveryEstimateReqDto, DeliveryEstimateResDto, ResponseStatus
from ecom.services.product_service import ProductService


class ProductController:
    def __init__(self, product_service: ProductService) -> None:
        self.product_service = product_service

    def get_estimated_delivery(self, request_dto: DeliveryEstimateReqDto) -> DeliveryEstimateResDto:
        try:
            expected = self.product_service.estimate_delivery_date(request_dto.product_id, request_dto.address_id)
            return DeliveryEstimateResDto(expected_delivery=expected, response_status=ResponseStatus.SUCCESS)
        except Exception:
            return DeliveryEstimateResDto(response_status=ResponseStatus.FAILURE)
