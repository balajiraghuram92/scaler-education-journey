from .model import Stock
from .strategies import TradingIndicatorStrategy


class StockTradingManager:
    """Context that computes an indicator with whichever strategy it is given.

    The old version branched on TradingStrategyType. Remove that: __init__ takes a
    strategy object and stores it, and calculate_indicator(stock) delegates to it.
    """

    def __init__(self, strategy: TradingIndicatorStrategy):
        raise NotImplementedError("Store the strategy")

    def calculate_indicator(self, stock: Stock) -> float:
        raise NotImplementedError("Delegate to the strategy")
