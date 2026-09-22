from .gift_card_service import GiftCardService
from ecom.models import GiftCard, LedgerEntry, TransactionType
from ecom.exceptions import NotFoundError
from ecom.utils import generate_gift_card_code
from django.utils import timezone


class GiftCardServiceImpl(GiftCardService):
    def create_gift_card(self, amount: float):
        gift_card_code = generate_gift_card_code()
        gift_card = GiftCard.objects.create(
            amount=amount,
            gift_card_code=gift_card_code,
            expires_at=timezone.now() + timezone.timedelta(days=365)
        )

        LedgerEntry.objects.create(
            amount=amount,
            transaction_type=TransactionType.CREDIT,
            gift_card=gift_card
        )

        return gift_card

    def redeem_gift_card(self, gift_card_code: str, amount: float):
        gift_card = GiftCard.objects.filter(gift_card_code=gift_card_code).first()
        if not gift_card:
            raise NotFoundError("Gift Card not found")

        if gift_card.amount < amount:
            raise ValueError("Insufficient balance")

        gift_card.amount -= amount
        gift_card.save()

        LedgerEntry.objects.create(
            amount=amount,
            transaction_type=TransactionType.DEBIT,
            gift_card=gift_card
        )

        return gift_card
