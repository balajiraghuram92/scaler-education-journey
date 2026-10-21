from abc import ABC, abstractmethod

from .model import Stock


class TradingIndicatorStrategy(ABC):
    """Strategy interface.

    Declare one abstract method: calculate_indicator(self, stock: Stock) -> float
    """


class MovingAverageStrategy(TradingIndicatorStrategy):
    """(price + previous_close) / 2"""


class MomentumStrategy(TradingIndicatorStrategy):
    """price - previous_close"""


class VolatilityStrategy(TradingIndicatorStrategy):
    """abs(price - previous_close)"""
