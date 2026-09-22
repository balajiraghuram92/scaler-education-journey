from ecom.services import GiftCardService
from ecom.dtos import ResponseStatus
from ecom.dtos import RedeemGiftCardRequestDto, RedeemGiftCardResponseDto
from ecom.dtos import CreateGiftCardRequestDto, CreateGiftCardResponseDto
from logging import getLogger, DEBUG
import traceback


class GiftCardController:
    gift_card_service: GiftCardService

    def __init__(
            self,
            gift_card_service: GiftCardService
    ):
        self.gift_card_service = gift_card_service
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)

    def create_gift_card(
            self,
            request_dto: CreateGiftCardRequestDto
    ):
        try:
            gift_card = self.gift_card_service.create_gift_card(
                request_dto.amount
            )
            response_dto = CreateGiftCardResponseDto(
                response_status=ResponseStatus.SUCCESS,
                gift_card=gift_card
            )
            return response_dto
        except Exception as e:
            self.logger.error(traceback.format_exc())
            response_dto = CreateGiftCardResponseDto(
                response_status=ResponseStatus.FAILURE
            )
            return response_dto

    def redeem_gift_card(
            self,
            request_dto: RedeemGiftCardRequestDto
    ):
        try:
            gift_card = self.gift_card_service.redeem_gift_card(
                request_dto.gift_card_code,
                request_dto.amount
            )
            response_dto = RedeemGiftCardResponseDto(
                response_status=ResponseStatus.SUCCESS,
                gift_card=gift_card
            )
            return response_dto
        except Exception as e:
            self.logger.error(traceback.format_exc())
            response_dto = RedeemGiftCardResponseDto(
                response_status=ResponseStatus.FAILURE
            )
            return response_dto
