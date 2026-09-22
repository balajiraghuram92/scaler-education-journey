from typing import List

from django.test import TestCase

from ecom.models import Product, ProductGroup
from ecom.services import RecommendationServiceImpl
from ecom.exceptions import NotFoundError


class TestRecService(TestCase):

    def setUp(self):
        self.rec_service = RecommendationServiceImpl()
        self.generate_data()

    def test_get_recommendations(self):
        product_id = self.data["products"][0].pk
        recommendations: List[int] = self.rec_service.get_recommendations(product_id)

        assert len(recommendations) > 0

    def test_get_recommendations_no_product(self):
        product_id = 1000
        with self.assertRaises(NotFoundError):
            self.rec_service.get_recommendations(product_id)

    def generate_data(self):

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

        product3 = Product.objects.create(
            name="test_product3",
            description="test_description3",
            price=300
        )

        product4 = Product.objects.create(
            name="test_product4",
            description="test_description4",
            price=400
        )

        product_group1 = ProductGroup.objects.create()
        product_group1.products.add(product1, product2, product3)

        product_group2 = ProductGroup.objects.create()
        product_group2.products.add(product3, product4)

        product_group3 = ProductGroup.objects.create()
        product_group3.products.add(product4)

        self.data = {
            "products": [product1, product2, product3, product4],
            "product_groups": [product_group1, product_group2, product_group3]
        }



