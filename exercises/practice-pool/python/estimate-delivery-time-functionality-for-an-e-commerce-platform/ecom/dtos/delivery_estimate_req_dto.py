from dataclasses import dataclass, field

@dataclass
class DeliveryEstimateReqDto:
    product_id: int
    address_id: int
