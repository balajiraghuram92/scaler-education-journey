from abc import ABC, abstractmethod

from .model import ClaimStatus
from .services import AutoProtectApi, TravelGuardApi


class TravelInsuranceAdapter(ABC):
    """Target interface: exactly two abstract methods.

    - add_claim(reference: str, amount: float) -> None
    - get_status(reference: str) -> ClaimStatus
    """


class AutoProtectAdapter(TravelInsuranceAdapter):
    """Wraps AutoProtectApi; keep the client in ``self.auto_protect_api`` (created in __init__).

    AutoProtect's add_claim takes only the amount. Its status may come back as a plain
    string or as an AutoProtectStatus Enum member: "APPROVED" maps to ClaimStatus.APPROVED,
    anything else to ClaimStatus.PENDING.
    """

    def __init__(self):
        raise NotImplementedError("Create self.auto_protect_api")


class TravelGuardAdapter(TravelInsuranceAdapter):
    """Wraps TravelGuardApi; keep the client in ``self.travel_guard_api`` (created in __init__).

    TravelGuard's submit_claim takes (claim_id, amount) and get_claim_status returns a
    status value; "APPROVED" maps to ClaimStatus.APPROVED, anything else to PENDING.
    """

    def __init__(self):
        raise NotImplementedError("Create self.travel_guard_api")
