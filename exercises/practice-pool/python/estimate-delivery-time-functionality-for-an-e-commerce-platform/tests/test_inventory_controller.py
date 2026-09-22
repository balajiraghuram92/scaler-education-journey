import datetime

from django.test import TestCase

from ecom.adapters import GoogleMapAdapter
from ecom.controllers import ProductController
from ecom.dtos import DeliveryEstimateReqDto, DeliveryEstimateResDto
from ecom.dtos import ResponseStatus
from ecom.models import User, Product, UserType, SellerAddress, DeliveryHub, DeliveryHubAddress, Seller, UserAddress
from ecom.services import ProductServiceImpl


class ProductControllerTest(TestCase):

    def setUp(self):
        self.map_adapter = GoogleMapAdapter()
        self.product_service = ProductServiceImpl(self.map_adapter)
        self.product_controller = ProductController(self.product_service)
        self.generate_data()

    def test_etd_success(self):
        user = self.data["customers"][0]
        address = user.addresses.first()
        product = self.data["products"][0]

        response: DeliveryEstimateResDto = self.product_controller.get_estimated_delivery(
            DeliveryEstimateReqDto(
                product_id=product.id,
                address_id=address.id
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS, "Response status is not success"
        assert response.expected_delivery > datetime.datetime.now(), "ETD is earlier than current time"

    def generate_data(self):
        customer1 = User.objects.create(
            name="test_customer",
            email="customer1@gmail.com",
            user_type=UserType.CUSTOMER
        )

        address1 = UserAddress.objects.create(
            user=customer1,
            street="test_street 1",
            city="test_city 1",
            country="test_country 1",
            zipcode=123456,
            latitude=123.123,
            longitude=123.123
        )

        address2 = UserAddress.objects.create(
            user=customer1,
            street="test_street 2",
            city="test_city 2",
            country="test_country 2",
            zipcode=623456,
            latitude=623.123,
            longitude=623.123
        )

        seller = Seller.objects.create(
            name="test_seller",
            email="seller1@gmail.com",
        )

        seller_address = SellerAddress.objects.create(
            seller=seller,
            street="seller_test_street",
            city="seller_test_city",
            country="test_country",
            zipcode=223456,
            latitude=223.123,
            longitude=223.123
        )

        delivery_hub = DeliveryHub.objects.create(
            name="test_hub",
        )

        delivery_hub_address = DeliveryHubAddress.objects.create(
            delivery_hub=delivery_hub,
            street="delivery_hub_street",
            city="test_city",
            country="test_country",
            zipcode=123456,
            latitude=123.123,
            longitude=124.123
        )

        product = Product.objects.create(
            name="test_product",
            description="test_description",
            price=100,
            seller=seller
        )

        self.data = {
            "customers": [customer1],
            "products": [product],
            "delivery_hubs": [delivery_hub],
        }



