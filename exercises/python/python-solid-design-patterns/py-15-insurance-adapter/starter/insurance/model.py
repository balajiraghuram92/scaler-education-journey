from enum import Enum


class AutoProtectStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class ClaimStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
