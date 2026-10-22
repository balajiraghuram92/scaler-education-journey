from dataclasses import dataclass
from enum import Enum


class TradingStrategyType(Enum):
    MOVING_AVERAGES = 1
    MOMENTUM = 2
    VOLATILITY = 3


@dataclass
class Stock:
    symbol: str
    price: float
    previous_close: float
