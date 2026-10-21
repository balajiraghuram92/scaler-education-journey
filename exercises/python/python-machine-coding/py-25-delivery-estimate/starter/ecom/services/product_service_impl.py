from datetime import datetime
from ecom.adapters.map_adapter import MapAdapter
from ecom.exceptions import AddressNotFoundError, ProductNotFoundError
from ecom.models import DeliveryHubAddress, Product, SellerAddress, UserAddress
from ecom.services.product_service import ProductService
from ecom.store import Store

class ProductServiceImpl(ProductService):

    def __init__(self, store: Store, map_adapter: MapAdapter) -> None:
        """Keep the store and the map adapter."""
        raise NotImplementedError('TODO: implement __init__')

    def estimate_delivery_date(self, product_id: int, address_id: int) -> datetime:
        """ProductNotFoundError for an unknown product; AddressNotFoundError for an unknown user address, a missing seller address or no hub for the zipcode of the user. Return datetime.now() + (seller address to hub) + (hub to user address), asking the adapter for each leg."""
        raise NotImplementedError('TODO: implement estimate_delivery_date')
