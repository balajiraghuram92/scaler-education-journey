from django.test import TestCase

from ecom.models import User, Product, Inventory, Notification, NotificationStatus
from ecom.services import NotificationServiceImpl, EmailServiceImpl, InventoryServiceImpl
from ecom.adapters import EmailAdapterImpl
from ecom.controllers import NotificationController
from ecom.dtos import RegisterUserNotifyReqDto, RegisterUserNotifyResDto
from ecom.dtos import ResponseStatus


class NotificationControllerTest(TestCase):

    def setUp(self):
        self.email_adapter = EmailAdapterImpl()
        self.email_service = EmailServiceImpl(self.email_adapter)
        self.inventory_service = InventoryServiceImpl(self.email_service)
        self.notification_service = NotificationServiceImpl()
        self.notification_controller = NotificationController(self.notification_service)

        self.generate_data()

    def test_register_user_success(self):

        product = self.data["products"][0]

        self.inventory_service.save_or_update_inventory(
            product.id,
            0
        )

        customer_id = self.data["customers"][0].id

        response: RegisterUserNotifyResDto = self.notification_controller.register_user(
            RegisterUserNotifyReqDto(
                user_id=customer_id,
                product_id=product.id
            )
        )

        notifications = Notification.objects.filter(
            product=product
        )

        assert response.response_status == ResponseStatus.SUCCESS, "User registration failed"
        assert response.notification_id is not None, "Notification id is not returned"
        assert len(notifications) == 1, "Notifications are not created"

    def test_register_user_fail_quantity_not_zero(self):

        product = self.data["products"][0]

        self.inventory_service.save_or_update_inventory(
            product.id,
            10
        )

        customer_id = self.data["customers"][0].id

        response: RegisterUserNotifyResDto = self.notification_controller.register_user(
            RegisterUserNotifyReqDto(
                user_id=customer_id,
                product_id=product.id
            )
        )

        assert response.response_status == ResponseStatus.FAILURE
        assert response.notification_id is None

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



