from .ads_service import AdsService
from ecom.models import Advertisement
from ecom.models import User
from ecom.exceptions import NotFoundError


class AdsServiceImpl(AdsService):

    def get_ad_for_user(self, user_id: int) -> Advertisement:

        user = User.objects.filter(id=user_id).first()
        if user is None:
            raise NotFoundError(f'User with id {user_id} not found')

        preferences = user.preferences.all()
        if len(preferences) == 0:
            return AdsServiceImpl.__get_random_ad()

        selected_ad = Advertisement.objects.filter(preference__in=preferences).order_by('?').first()

        if selected_ad is None:
            return AdsServiceImpl.__get_random_ad()

        return selected_ad

    @classmethod
    def __get_random_ad(cls) -> Advertisement:
        return Advertisement.objects.order_by('?').first()
