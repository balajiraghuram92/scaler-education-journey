from django.test import TestCase

from ecom.exceptions import NotFoundError
from ecom.models import GiftCard, LedgerEntry
from ecom.services import GiftCardServiceImpl


class TestGiftCardService(TestCase):

    def setUp(self):
        self.gift_card_service = GiftCardServiceImpl()

    def test_create_gift_card(self):
        gift_card = self.gift_card_service.create_gift_card(100)

        entries = LedgerEntry.objects.filter(gift_card=gift_card)

        self.assertEqual(len(entries), 1)
        self.assertEqual(gift_card.amount, 100)
        self.assertIsNotNone(gift_card.gift_card_code)
        self.assertIsNotNone(gift_card.expires_at)
        assert len(gift_card.gift_card_code) == 10

    def test_redeem_gift_card_success(self):
        gift_card = self.gift_card_service.create_gift_card(100)
        self.gift_card_service.redeem_gift_card(gift_card.gift_card_code, 50)

        updated_gift_card = GiftCard.objects.get(id=gift_card.id)

        assert updated_gift_card.amount == 50

    def test_redeem_gift_card_not_found(self):
        with self.assertRaises(NotFoundError):
            self.gift_card_service.redeem_gift_card("invalid_code", 50)

    def test_redeem_gift_card_insufficient_balance(self):
        gift_card = self.gift_card_service.create_gift_card(100)
        with self.assertRaises(ValueError):
            self.gift_card_service.redeem_gift_card(gift_card.gift_card_code, 150)
