from datetime import datetime

from ecom.adapters.map_adapter import MapAdapter
from ecom.exceptions import AddressNotFoundError, ProductNotFoundError
from ecom.models import DeliveryHubAddress, Product, SellerAddress, UserAddress
from ecom.services.product_service import ProductService
from ecom.store import Store


class ProductServiceImpl(ProductService):
    def __init__(self, store: Store, map_adapter: MapAdapter) -> None:
        self.store = store
        self.map_adapter = map_adapter

    def estimate_delivery_date(self, product_id: int, address_id: int) -> datetime:
        product = self.store.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")

        user_address = self.store.get(UserAddress, address_id)
        if user_address is None:
            raise AddressNotFoundError("Delivery Address not found")

        seller_address = None
        if product.seller is not None:
            seller_address = self.store.first(SellerAddress, seller=product.seller)
        if seller_address is None:
            raise AddressNotFoundError("Seller Address not found")

        hub = self.store.first(DeliveryHubAddress, zipcode=user_address.zipcode)
        if hub is None:
            raise AddressNotFoundError("Delivery Hub Address not found")

        seller_to_hub = self.map_adapter.get_estimated_time(
            seller_address.latitude, seller_address.longitude, hub.latitude, hub.longitude)
        hub_to_customer = self.map_adapter.get_estimated_time(
            hub.latitude, hub.longitude, user_address.latitude, user_address.longitude)
        return datetime.now() + seller_to_hub + hub_to_customer
