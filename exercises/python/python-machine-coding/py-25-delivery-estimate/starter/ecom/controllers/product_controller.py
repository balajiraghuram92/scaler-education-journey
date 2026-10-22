from ecom.dtos import DeliveryEstimateReqDto, DeliveryEstimateResDto, ResponseStatus
from ecom.services.product_service import ProductService

class ProductController:

    def __init__(self, product_service: ProductService) -> None:
        """Keep the product service."""
        raise NotImplementedError('TODO: implement __init__')

    def get_estimated_delivery(self, request_dto: DeliveryEstimateReqDto) -> DeliveryEstimateResDto:
        """DeliveryEstimateResDto(expected_delivery, SUCCESS), or FAILURE on any exception."""
        raise NotImplementedError('TODO: implement get_estimated_delivery')
