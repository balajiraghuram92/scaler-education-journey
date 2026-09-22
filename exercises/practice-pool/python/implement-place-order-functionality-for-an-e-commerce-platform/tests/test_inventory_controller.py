from django.test import TestCase

from ecom.models import User, Product, UserType, Inventory
from ecom.services import OrderServiceImpl
from ecom.controllers import OrderController
from ecom.dtos import PlaceOrderReqDto, PlaceOrderResDto, ResponseStatus


class TestOrderController(TestCase):

    def setUp(self):
        self.order_service = OrderServiceImpl()
        self.order_controller = OrderController(self.order_service)
        self.generate_data()

    def test_create_order_success(self):
        customer = self.data["customers"][0]
        product1 = self.data["products"][0]
        product2 = self.data["products"][1]

        product1_quantity = Inventory.objects.filter(product=product1).first().quantity
        product2_quantity = Inventory.objects.filter(product=product2).first().quantity

        response: PlaceOrderResDto =  self.order_controller.place_order(
            PlaceOrderReqDto(
                user_id=customer.id,
                product_ids_with_quantity=[(product1.id, 2), (product2.id, 3)]
            )
        )

        expected_quantities = [product1_quantity - 2, product2_quantity - 3]

        product1_quantity_new = Inventory.objects.filter(product=product1).first().quantity
        product2_quantity_new = Inventory.objects.filter(product=product2).first().quantity

        assert product1_quantity_new == expected_quantities[0], "Product1 quantity is not updated"
        assert product2_quantity_new == expected_quantities[1], "Product2 quantity is not updated"

    def test_create_order_fail_not_enough_quantity(self):
        customer = self.data["customers"][0]
        product1 = self.data["products"][0]
        product2 = self.data["products"][1]

        product1_quantity = Inventory.objects.filter(product=product1).first().quantity
        product2_quantity = Inventory.objects.filter(product=product2).first().quantity

        response: PlaceOrderResDto = self.order_controller.place_order(
            PlaceOrderReqDto(
                user_id=customer.id,
                product_ids_with_quantity=[(product1.id, 10), (product2.id, 10)]
            )
        )

        assert response.response_status == ResponseStatus.FAILURE, "Order should fail"
        assert response.order is None, "Order should not be created"

        product1_quantity_new = Inventory.objects.filter(product=product1).first().quantity
        product2_quantity_new = Inventory.objects.filter(product=product2).first().quantity

        assert product1_quantity_new == product1_quantity, "Product1 quantity should not be updated"
        assert product2_quantity_new == product2_quantity, "Product2 quantity should not be updated"

    def generate_data(self):

        customer1 = User.objects.create(
            name="test_customer",
            email="customer1@gmail.com",
            user_type=UserType.CUSTOMER
        )

        product1 = Product.objects.create(
            name="test_product1",
            description="test_description1",
            price=100
        )

        product2 = Product.objects.create(
            name="test_product2",
            description="test_description2",
            price=200
        )

        Inventory.objects.create(
            product=product1,
            quantity=5
        )

        Inventory.objects.create(
            product=product2,
            quantity=7
        )

        self.data = {
            "customers": [customer1],
            "products": [product1, product2]
        }
