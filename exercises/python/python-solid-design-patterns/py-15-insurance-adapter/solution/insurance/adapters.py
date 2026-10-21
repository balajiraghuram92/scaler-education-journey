from abc import ABC, abstractmethod

from .model import ClaimStatus
from .services import AutoProtectApi, TravelGuardApi


def _to_claim_status(status) -> ClaimStatus:
    # Vendors return either a plain string or an Enum member; normalise before comparing.
    value = getattr(status, "value", status)
    return ClaimStatus.APPROVED if value == "APPROVED" else ClaimStatus.PENDING


class TravelInsuranceAdapter(ABC):
    @abstractmethod
    def add_claim(self, reference: str, amount: float) -> None:
        pass

    @abstractmethod
    def get_status(self, reference: str) -> ClaimStatus:
        pass


class AutoProtectAdapter(TravelInsuranceAdapter):
    def __init__(self):
        self.auto_protect_api = AutoProtectApi()

    def add_claim(self, reference: str, amount: float) -> None:
        self.auto_protect_api.add_claim(amount)

    def get_status(self, reference: str) -> ClaimStatus:
        return _to_claim_status(self.auto_protect_api.get_status(reference))


class TravelGuardAdapter(TravelInsuranceAdapter):
    def __init__(self):
        self.travel_guard_api = TravelGuardApi()

    def add_claim(self, reference: str, amount: float) -> None:
        self.travel_guard_api.submit_claim(reference, amount)

    def get_status(self, reference: str) -> ClaimStatus:
        return _to_claim_status(self.travel_guard_api.get_claim_status(reference))
