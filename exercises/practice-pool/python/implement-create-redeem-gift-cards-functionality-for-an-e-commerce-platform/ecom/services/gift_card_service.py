from abc import ABC, abstractmethod


class GiftCardService(ABC):

    @abstractmethod
    def create_gift_card(
            self,
            amount: float
    ):
        pass

    @abstractmethod
    def redeem_gift_card(
            self,
            gift_card_code: str,
            amount: float
    ):
        pass
