from django.test import TestCase

from ecom.models import User, Preference, Advertisement
from ecom.services import AdsServiceImpl
from ecom.controllers import AdsController
from ecom.dtos import GetAdvertisementForUserRequestDto, GetAdvertisementForUserResponseDto
from ecom.dtos import ResponseStatus


class AdsControllerTest(TestCase):

    def setUp(self):
        self.ads_service = AdsServiceImpl()
        self.ads_controller = AdsController(self.ads_service)
        self.generate_data()

    def test_get_ad_for_user_with_ads_success(self):
        user = self.data["users"][0]

        response: GetAdvertisementForUserResponseDto = self.ads_controller.get_ad_for_user(
            GetAdvertisementForUserRequestDto(
                user_id=user.id
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS

        ad = response.ad
        assert ad is not None, "Ad is None"
        assert ad.preference in user.preferences.all(), "Ad preference is not in user preferences"

    def test_get_ad_for_user_with_no_pref_success(self):
        user = self.data["users"][1]

        response: GetAdvertisementForUserResponseDto = self.ads_controller.get_ad_for_user(
            GetAdvertisementForUserRequestDto(
                user_id=user.id
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS
        ad = response.ad
        assert ad is not None, "Ad is None"
        assert ad.preference not in user.preferences.all(), "Ad preference is not in user preferences"

    def test_get_ad_for_pref_with_no_ads_success(self):
        user = self.data["users"][2]

        response: GetAdvertisementForUserResponseDto = self.ads_controller.get_ad_for_user(
            GetAdvertisementForUserRequestDto(
                user_id=user.id
            )
        )

        ad = response.ad
        assert response.response_status == ResponseStatus.SUCCESS
        assert ad is not None, "Ad is None"
        assert ad.preference not in user.preferences.all(), "Ad preference is not in user preferences"

    def test_get_ad_for_invalid_user(self):
        response: GetAdvertisementForUserResponseDto = self.ads_controller.get_ad_for_user(
            GetAdvertisementForUserRequestDto(
                user_id=100
            )
        )

        assert response.response_status == ResponseStatus.FAILURE

    def generate_data(self):

        # user1 has 2 preferences and 2 ads
        # user2 has no preferences
        # user3 has 1 preference and 0 ads

        user1 = User.objects.create(
            name="test_admin",
            email="admin1@gmail.com",
        )

        preference1 = Preference.objects.create(
            category="test_preference1"

        )

        preference2 = Preference.objects.create(
            category="test_preference2"
        )

        user1.preferences.add(preference1)
        user1.preferences.add(preference2)

        ad1 = Advertisement.objects.create(
            name="ad1",
            description="ad1 description",
            preference=preference1
        )

        ad2 = Advertisement.objects.create(
            name="ad2",
            description="ad2 description",
            preference=preference1
        )

        user2 = User.objects.create(
            name="test_user2",
            email="testuser2@gmail.com"
        )

        user3 = User.objects.create(
            name="test_user3",
            email="testuser3@gmail.com"
        )

        user3.preferences.add(preference2)

        self.data = {
            "users": [user1, user2, user3],
        }
