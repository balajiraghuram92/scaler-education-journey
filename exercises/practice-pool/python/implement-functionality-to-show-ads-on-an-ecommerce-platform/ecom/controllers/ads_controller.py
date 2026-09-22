from ecom.services import AdsService
from ecom.dtos import GetAdvertisementForUserRequestDto, GetAdvertisementForUserResponseDto
from ecom.dtos import ResponseStatus
from logging import getLogger, DEBUG
import traceback


class AdsController:
    ads_service: AdsService

    def __init__(
            self,
            ads_service: AdsService
    ):
        self.ads_service = ads_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def get_ad_for_user(
            self,
            request_dto: GetAdvertisementForUserRequestDto
    ):
        try:
            ad = self.ads_service.get_ad_for_user(
                request_dto.user_id
            )

            response = GetAdvertisementForUserResponseDto(
                response_status=ResponseStatus.SUCCESS,
                ad=ad
            )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            response = GetAdvertisementForUserResponseDto(
                response_status=ResponseStatus.FAILURE
            )

        return response
