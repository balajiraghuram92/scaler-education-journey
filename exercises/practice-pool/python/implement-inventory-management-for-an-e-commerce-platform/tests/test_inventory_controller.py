from django.test import TestCase

from ecom.controllers import InventoryController
from ecom.dtos import CreateUpdateInventoryReqDto, CreateUpdateInventoryResponseDto
from ecom.dtos import ResponseStatus
from ecom.models import User, Product, UserType
from ecom.services import InventoryServiceImpl


class InventoryControllerTest(TestCase):

    def setUp(self):
        self.inventory_service = InventoryServiceImpl()
        self.inventory_controller = InventoryController(self.inventory_service)

        self.generate_data()

    def test_create_inventory_success(self):
        admin = self.data["admins"][0]
        product = self.data["products"][0]
        quantity = 10

        response: CreateUpdateInventoryResponseDto = self.inventory_controller.create_or_update_inventory(
            CreateUpdateInventoryReqDto(
                user_id=admin.id,
                product_id=product.id,
                quantity=quantity
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS, "Response status is not success"
        assert response.inventory.product == product, "Product is not same as expected"

    def test_update_inventory_failure_not_admin_user(self):
        customer = self.data["customers"][0]
        product = self.data["products"][0]
        quantity = 10

        response: CreateUpdateInventoryResponseDto = self.inventory_controller.create_or_update_inventory(
            CreateUpdateInventoryReqDto(
                user_id=customer.id,
                product_id=product.id,
                quantity=quantity
            )
        )

        assert response.response_status == ResponseStatus.FAILURE
        assert response.inventory is None

    def generate_data(self):
        admin1 = User.objects.create(
            name="test_admin",
            email="admin1@gmail.com",
            user_type=UserType.ADMIN
        )

        customer1 = User.objects.create(
            name="test_customer",
            email="customer1@gmail.com",
            user_type=UserType.CUSTOMER
        )

        product = Product.objects.create(
            name="test_product",
            description="test_description",
            price=100
        )

        self.data = {
            "admins": [admin1],
            "customers": [customer1],
            "products": [product]
        }
