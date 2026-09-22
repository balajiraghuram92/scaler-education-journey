from abc import ABC, abstractmethod
from ecom.models import Advertisement


class AdsService(ABC):

    @abstractmethod
    def get_ad_for_user(
            self,
            user_id: int
    ) -> Advertisement:
        pass
