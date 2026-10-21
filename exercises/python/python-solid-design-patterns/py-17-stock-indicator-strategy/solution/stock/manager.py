from .model import Stock
from .strategies import TradingIndicatorStrategy


class StockTradingManager:
    def __init__(self, strategy: TradingIndicatorStrategy):
        self.strategy = strategy

    def calculate_indicator(self, stock: Stock) -> float:
        return self.strategy.calculate_indicator(stock)
