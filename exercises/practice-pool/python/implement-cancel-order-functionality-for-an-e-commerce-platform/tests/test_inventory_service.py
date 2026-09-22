from django.test import TestCase

import pytest

from ecom.exceptions import UnauthorizedAccessError, UserNotFoundError, OrderCannotBeCancelledError
from ecom.models import User, Product, UserType, Inventory, Order, OrderItem
from ecom.models.order_status import OrderStatus
from ecom.services import OrderServiceImpl


class TestInventoryService(TestCase):

    def setUp(self):
        print("Setting up data")
        self.order_service = OrderServiceImpl()
        self.generate_data()

    def test_create_inventory_success(self):
        customer = self.data["customers"][0]
        product1 = self.data["products"][0]
        product2 = self.data["products"][1]

        order = Order.objects.create(
            user=customer,
            order_status=OrderStatus.PLACED,
        )

        OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=2
        )

        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=3
        )

        product1_quantity = Inventory.objects.filter(product=product1).first().quantity
        product2_quantity = Inventory.objects.filter(product=product2).first().quantity

        self.order_service.cancel_order(
            customer.id,
            order.id
        )

        expected_quantities = [product1_quantity + 2, product2_quantity + 3]

        product1_quantity_new = Inventory.objects.filter(product=product1).first().quantity
        product2_quantity_new = Inventory.objects.filter(product=product2).first().quantity

        assert product1_quantity_new == expected_quantities[0], "Product1 quantity is not updated"
        assert product2_quantity_new == expected_quantities[1], "Product2 quantity is not updated"

    def test_create_inventory_fail_shipped(self):
        customer = self.data["customers"][0]
        product1 = self.data["products"][0]
        product2 = self.data["products"][1]

        order = Order.objects.create(
            user=customer,
            order_status=OrderStatus.SHIPPED,
        )

        OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=2
        )

        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=3
        )

        with self.assertRaises(OrderCannotBeCancelledError):
            self.order_service.cancel_order(
                customer.id,
                order.id
            )

    def test_create_inventory_fail_cancelled(self):

        customer = self.data["customers"][0]
        product1 = self.data["products"][0]
        product2 = self.data["products"][1]

        order = Order.objects.create(
            user=customer,
            order_status=OrderStatus.CANCELLED,
        )

        OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=2
        )

        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=3
        )

        with self.assertRaises(OrderCannotBeCancelledError):
            self.order_service.cancel_order(
                customer.id,
                order.id
            )

    def test_create_inventory_fail_delivered(self):
        customer = self.data["customers"][0]
        product1 = self.data["products"][0]
        product2 = self.data["products"][1]

        order = Order.objects.create(
            user=customer,
            order_status=OrderStatus.DELIVERED,
        )

        OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=2
        )

        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=3
        )

        with self.assertRaises(OrderCannotBeCancelledError):
            self.order_service.cancel_order(
                customer.id,
                order.id
            )

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
            quantity=10
        )

        Inventory.objects.create(
            product=product2,
            quantity=20
        )

        self.data = {
            "customers": [customer1],
            "products": [product1, product2]
        }



