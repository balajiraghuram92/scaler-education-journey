from abc import ABC, abstractmethod

from .model import Stock


class TradingIndicatorStrategy(ABC):
    @abstractmethod
    def calculate_indicator(self, stock: Stock) -> float:
        pass


class MovingAverageStrategy(TradingIndicatorStrategy):
    def calculate_indicator(self, stock: Stock) -> float:
        return (stock.price + stock.previous_close) / 2


class MomentumStrategy(TradingIndicatorStrategy):
    def calculate_indicator(self, stock: Stock) -> float:
        return stock.price - stock.previous_close


class VolatilityStrategy(TradingIndicatorStrategy):
    def calculate_indicator(self, stock: Stock) -> float:
        return abs(stock.price - stock.previous_close)
