from django.test import TestCase

from ecom.exceptions import UnauthorizedAccessError, UserNotFoundError
from ecom.models import User, Product, UserType, Inventory
from ecom.services import InventoryServiceImpl


class InventoryServiceTest(TestCase):

    def setUp(self):
        self.inventory_service = InventoryServiceImpl()
        self.generate_data()

    def test_create_inventory_success(self):
        admin = self.data["admins"][0]
        product = self.data["products"][0]
        quantity = 10

        inventory = self.inventory_service.create_or_update_inventory(
            admin.id,
            product.id,
            quantity
        )

        assert inventory.product == product, "Product is not same as expected"
        assert inventory.quantity == quantity, "Quantity is not same as expected"

    def test_update_inventory_failure_not_admin_user(self):
        customer = self.data["customers"][0]
        product = self.data["products"][0]
        quantity = 10

        with self.assertRaises(UnauthorizedAccessError):
            self.inventory_service.create_or_update_inventory(
                customer.id,
                product.id,
                quantity
            )

    def test_update_inventory_failure_invalid_user(self):
        product = self.data["products"][0]
        quantity = 10

        with self.assertRaises(UserNotFoundError):
            self.inventory_service.create_or_update_inventory(
                100,
                product.id,
                quantity
            )

    def test_delete_inventory_success(self):
        product = self.data["products"][0]
        quantity = 10

        Inventory.objects.create(
            product=product,
            quantity=quantity
        )

        inventory = Inventory.objects.filter(
            product=product
        ).first()

        assert inventory is not None, "Inventory is not created"

        admin = self.data["admins"][0]

        self.inventory_service.delete_inventory(
            admin.id,
            product.id,
        )

        inventory = Inventory.objects.filter(
            product=product
        ).first()

        assert inventory is None, "Inventory is not deleted"


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



