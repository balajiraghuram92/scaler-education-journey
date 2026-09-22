from .product_service import ProductService
from ecom.models import Product, UserAddress, SellerAddress, DeliveryHubAddress
from ecom.exceptions import AddressNotFoundError, ProductNotFoundError, UserNotFoundError
from datetime import datetime

from ecom.adapters import MapAdapter


class ProductServiceImpl(ProductService):
    map_adapter: MapAdapter

    def __init__(
            self,
            map_adapter: MapAdapter
    ):
        self.map_adapter = map_adapter

    def estimate_delivery_date(
            self,
            product_id: int,
            address_id: int
    ) -> datetime:

        product = Product.objects.filter(pk=product_id).first()

        if not product:
            raise ProductNotFoundError("Product not found")

        user_address = UserAddress.objects.filter(pk=address_id).first()
        if not user_address:
            raise AddressNotFoundError("Delivery Address not found")

        seller_address = SellerAddress.objects.filter(
            seller=product.seller
        ).first()
        if not seller_address:
            raise AddressNotFoundError("Seller Address not found")

        delivery_hub_address = DeliveryHubAddress.objects.filter(
            zipcode=user_address.zipcode
        ).first()
        if not delivery_hub_address:
            raise AddressNotFoundError("Delivery Hub Address not found")

        seller_to_delivery_hub = self.map_adapter.get_estimated_time(
            seller_address.latitude,
            seller_address.longitude,
            delivery_hub_address.latitude,
            delivery_hub_address.longitude
        )

        delivery_hub_to_customer = self.map_adapter.get_estimated_time(
            delivery_hub_address.latitude,
            delivery_hub_address.longitude,
            user_address.latitude,
            user_address.longitude
        )

        total_time = seller_to_delivery_hub + delivery_hub_to_customer

        return datetime.now() + total_time



