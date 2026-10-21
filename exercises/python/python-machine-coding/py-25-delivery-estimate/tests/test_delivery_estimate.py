from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from ecom.adapters.google_map_adapter import GoogleMapAdapter
from ecom.adapters.map_adapter import MapAdapter
from ecom.controllers.product_controller import ProductController
from ecom.dtos import DeliveryEstimateReqDto, ResponseStatus
from ecom.exceptions import AddressNotFoundError, ProductNotFoundError
from ecom.libraries.google_maps_api import GoogleMapsApi
from ecom.libraries.google_models import GoogleLocation
from ecom.models import DeliveryHubAddress, Product, Seller, SellerAddress, User, UserAddress
from ecom.services.product_service_impl import ProductServiceImpl
from ecom.store import Store

NOW = datetime(2026, 3, 1, 9, 0, 0)


class FakeAdapter(MapAdapter):
    """Travel time = 10 minutes per unit of latitude difference, so every leg is distinguishable."""

    def __init__(self):
        self.calls = []

    def get_estimated_time(self, source_lat, source_long, destination_lat, destination_long):
        self.calls.append((source_lat, source_long, destination_lat, destination_long))
        return timedelta(minutes=10 * abs(destination_lat - source_lat))


class World:
    def __init__(self):
        self.store = Store()
        self.seller = self.store.add(Seller("Acme"))
        self.product = self.store.add(Product("Phone", self.seller))
        self.user = self.store.add(User("Asha"))
        self.seller_address = self.store.add(SellerAddress(self.seller, 10.0, 70.0))
        self.hub_560 = self.store.add(DeliveryHubAddress("560001", 13.0, 77.0))
        self.hub_110 = self.store.add(DeliveryHubAddress("110001", 28.0, 77.0))
        self.address = self.store.add(UserAddress(self.user, "560001", 12.0, 77.5))
        self.adapter = FakeAdapter()
        self.service = ProductServiceImpl(self.store, self.adapter)


@freeze_time(NOW)
def test_estimate_is_now_plus_both_legs():
    w = World()
    result = w.service.estimate_delivery_date(w.product.id, w.address.id)
    # seller (10) -> hub (13): 3 * 10 = 30 min; hub (13) -> user (12): 1 * 10 = 10 min
    assert result == NOW + timedelta(minutes=40)


def test_legs_use_the_right_coordinates_in_order():
    w = World()
    w.service.estimate_delivery_date(w.product.id, w.address.id)
    assert w.adapter.calls == [(10.0, 70.0, 13.0, 77.0), (13.0, 77.0, 12.0, 77.5)]


def test_hub_is_chosen_by_the_users_zipcode():
    w = World()
    w.address.zipcode = "110001"
    w.service.estimate_delivery_date(w.product.id, w.address.id)
    assert w.adapter.calls[0][2:] == (28.0, 77.0), "the first leg must end at the 110001 hub"
    assert w.adapter.calls[1][:2] == (28.0, 77.0)


def test_missing_data_raises_the_right_error():
    w = World()
    with pytest.raises(ProductNotFoundError):
        w.service.estimate_delivery_date(999, w.address.id)
    with pytest.raises(AddressNotFoundError):
        w.service.estimate_delivery_date(w.product.id, 999)
    w.store.delete(w.seller_address)
    with pytest.raises(AddressNotFoundError):
        w.service.estimate_delivery_date(w.product.id, w.address.id)
    w.store.add(w.seller_address)
    w.address.zipcode = "999999"
    with pytest.raises(AddressNotFoundError):
        w.service.estimate_delivery_date(w.product.id, w.address.id)
    assert w.adapter.calls == [], "no travel time may be requested when data is missing"


@freeze_time(NOW)
def test_service_only_depends_on_the_adapter_interface():
    w = World()

    class Constant(MapAdapter):
        def get_estimated_time(self, *coordinates):
            return timedelta(hours=1)

    other = ProductServiceImpl(w.store, Constant())
    assert other.estimate_delivery_date(w.product.id, w.address.id) == NOW + timedelta(hours=2)
    assert w.service.estimate_delivery_date(w.product.id, w.address.id) == NOW + timedelta(minutes=40)


def test_google_adapter_wraps_the_sdk(monkeypatch):
    seen = []

    def fake_estimate(self, source, destination):
        seen.append((source, destination))
        return timedelta(minutes=17)

    monkeypatch.setattr(GoogleMapsApi, "estimate", fake_estimate)
    result = GoogleMapAdapter().get_estimated_time(1.5, 2.5, 3.5, 4.5)
    assert result == timedelta(minutes=17)
    assert seen == [(GoogleLocation(1.5, 2.5), GoogleLocation(3.5, 4.5))]


def test_google_adapter_implements_the_interface():
    assert issubclass(GoogleMapAdapter, MapAdapter)
    assert isinstance(GoogleMapAdapter().get_estimated_time(0.0, 0.0, 0.1, 0.0), timedelta)
    with pytest.raises(TypeError):
        MapAdapter()


@freeze_time(NOW)
def test_controller_responses():
    w = World()
    controller = ProductController(w.service)
    ok = controller.get_estimated_delivery(DeliveryEstimateReqDto(w.product.id, w.address.id))
    assert ok.response_status is ResponseStatus.SUCCESS
    assert ok.expected_delivery == NOW + timedelta(minutes=40)
    for request in (DeliveryEstimateReqDto(999, w.address.id), DeliveryEstimateReqDto(w.product.id, 999)):
        res = controller.get_estimated_delivery(request)
        assert res.response_status is ResponseStatus.FAILURE
        assert res.expected_delivery is None
