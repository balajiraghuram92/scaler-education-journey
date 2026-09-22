import datetime

from django.test import TestCase

from ecom.adapters import MapAdapter, GoogleMapAdapter
from ecom.models import User, Product, UserType, DeliveryHub
from ecom.models import Seller, SellerAddress, DeliveryHubAddress
from ecom.services import ProductServiceImpl
from ecom.models import UserAddress


class InventoryServiceTest(TestCase):

    def setUp(self):
        self.map_adapter = GoogleMapAdapter()
        self.product_service = ProductServiceImpl(self.map_adapter)
        self.generate_data()

    def test_get_etd_success(self):
        user = self.data["customers"][0]
        address = user.addresses.first()
        product = self.data["products"][0]

        delivery_date = self.product_service.estimate_delivery_date(
            product.id,
            address.id
        )

        assert delivery_date is not None
        assert delivery_date > datetime.datetime.now()

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



