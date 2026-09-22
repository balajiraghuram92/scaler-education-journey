from typing import List

from .recommendation_service import RecommendationService
from ecom.models import Product, ProductGroup
from ecom.exceptions import NotFoundError


class RecommendationServiceImpl(RecommendationService):

    def get_recommendations(self, product_id: int) -> List[int]:

        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")

        product_groups = ProductGroup.objects.filter(products=product)
        recommendations = []
        for product_group in product_groups:
            for product in product_group.products.all():
                recommendations.append(product.id)
        return recommendations
