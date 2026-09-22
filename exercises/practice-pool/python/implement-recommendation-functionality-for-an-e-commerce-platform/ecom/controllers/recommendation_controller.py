from ecom.services import RecommendationService
from ecom.dtos import GenerateRecommendationsRequestDto, GenerateRecommendationsResponseDto, ResponseStatus
from logging import getLogger, DEBUG
import traceback


class RecommendationsController:
    rec_service: RecommendationService

    def __init__(
            self,
            rec_service: RecommendationService
    ):
        self.rec_service = rec_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def generate_recommendations(
            self,
            request_dto: GenerateRecommendationsRequestDto
    ):
        try:
            recommendations = self.rec_service.get_recommendations(
                request_dto.product_id
            )

            response = GenerateRecommendationsResponseDto(
                response_status=ResponseStatus.SUCCESS,
                recommendations=recommendations
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = GenerateRecommendationsResponseDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
