from django.test import TestCase

from ecom.exceptions import UnauthorizedAccessError, UserNotFoundError, ProductInStockError
from ecom.models import User, Product, Inventory, Notification, NotificationStatus
from ecom.services import NotificationServiceImpl, EmailServiceImpl, InventoryServiceImpl
from ecom.adapters import EmailAdapterImpl


class NotificationServiceTest(TestCase):

    def setUp(self):
        self.email_adapter = EmailAdapterImpl()
        self.email_service = EmailServiceImpl(self.email_adapter)
        self.inventory_service = InventoryServiceImpl(self.email_service)
        self.notification_service = NotificationServiceImpl()
        self.generate_data()

    def test_register_user_success(self):

        product = self.data["products"][0]

        self.inventory_service.save_or_update_inventory(
            product.id,
            0
        )

        for customer in self.data["customers"]:

            notification = self.notification_service.register_user(
                customer.id,
                product.id
            )

        notifications = Notification.objects.filter(
            product=product
        )

        assert len(notifications) == 2, "Notifications are not created"

    def test_register_user_fail_quantity_not_zero(self):

        product = self.data["products"][0]

        self.inventory_service.save_or_update_inventory(
            product.id,
            10
        )

        with self.assertRaises(ProductInStockError):
            for customer in self.data["customers"]:
                notification = self.notification_service.register_user(
                    customer.id,
                    product.id
                )

    def test_register_user_notify_after_update(self):

        product = self.data["products"][0]

        self.inventory_service.save_or_update_inventory(
            product.id,
            0
        )

        for customer in self.data["customers"]:
            notification = self.notification_service.register_user(
                customer.id,
                product.id
            )

        self.inventory_service.save_or_update_inventory(
            product.id,
            10
        )

        notifications = Notification.objects.filter(
            product=product,
            status=NotificationStatus.SENT
        )

        assert len(notifications) == 2, "Notifications are not sent after inventory update"

    def generate_data(self):

        customer1 = User.objects.create(
            name="test_customer1",
            email="customer1@gmail.com"
        )

        customer2 = User.objects.create(
            name="test_customer2",
            email="customer2@gmail.com"
        )

        product = Product.objects.create(
            name="test_product",
            description="test_description",
            price=100
        )

        inventory = Inventory.objects.create(
            product=product,
            quantity=10
        )

        self.data = {
            "customers": [customer1, customer2],
            "products": [product],
        }



