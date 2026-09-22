from django.test import TestCase

from django.test import TestCase

from ecom.controllers import GiftCardController
from ecom.exceptions import NotFoundError
from ecom.models import GiftCard
from ecom.services import GiftCardServiceImpl
from ecom.dtos import CreateGiftCardRequestDto, CreateGiftCardResponseDto, RedeemGiftCardRequestDto, RedeemGiftCardResponseDto
from ecom.dtos import ResponseStatus


class TestGiftCardController(TestCase):

    def setUp(self):
        self.gift_card_service = GiftCardServiceImpl()
        self.gift_card_controller = GiftCardController(self.gift_card_service)

    def test_create_gift_card(self):

        response_dto = self.gift_card_controller.create_gift_card(
            CreateGiftCardRequestDto(
                amount=100
            )
        )

        gift_card = response_dto.gift_card
        self.assertEqual(gift_card.amount, 100)
        self.assertIsNotNone(gift_card.gift_card_code)
        self.assertIsNotNone(gift_card.expires_at)
        assert len(gift_card.gift_card_code) == 10

    def test_redeem_gift_card_success(self):
        response_dto_create = self.gift_card_controller.create_gift_card(
            CreateGiftCardRequestDto(
                amount=100
            )
        )

        assert response_dto_create.response_status == ResponseStatus.SUCCESS

        gift_card = response_dto_create.gift_card

        response_dto_redeem = self.gift_card_controller.redeem_gift_card(
            RedeemGiftCardRequestDto(
                amount=50,
                gift_card_code=gift_card.gift_card_code
            )
        )

        assert response_dto_redeem.response_status == ResponseStatus.SUCCESS
        updated_gift_card = GiftCard.objects.get(id=gift_card.id)
        assert updated_gift_card.amount == 50

    def test_redeem_gift_card_not_found(self):
        response_dto_redeem = self.gift_card_controller.redeem_gift_card(
            RedeemGiftCardRequestDto(
                amount=50,
                gift_card_code="invalid_code"
            )
        )

        assert response_dto_redeem.response_status == ResponseStatus.FAILURE

    def test_redeem_gift_card_insufficient_balance(self):
        response_dto_create = self.gift_card_controller.create_gift_card(
            CreateGiftCardRequestDto(
                amount=100
            )
        )

        gift_card = response_dto_create.gift_card

        response_dto_redeem = self.gift_card_controller.redeem_gift_card(
            RedeemGiftCardRequestDto(
                amount=150,
                gift_card_code=gift_card.gift_card_code
            )
        )

        assert response_dto_redeem.response_status == ResponseStatus.FAILURE
