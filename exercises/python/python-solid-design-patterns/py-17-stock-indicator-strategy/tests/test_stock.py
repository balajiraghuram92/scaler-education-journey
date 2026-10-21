import inspect
from types import SimpleNamespace

import pytest

from stock.manager import StockTradingManager
from stock.model import Stock
from stock.strategies import (
    MomentumStrategy,
    MovingAverageStrategy,
    TradingIndicatorStrategy,
    VolatilityStrategy,
)

CONCRETE = (MovingAverageStrategy, MomentumStrategy, VolatilityStrategy)


def test_interface_is_abstract_and_declares_calculate_indicator():
    assert inspect.isabstract(TradingIndicatorStrategy), "TradingIndicatorStrategy must be an ABC with an abstract method"
    assert "calculate_indicator" in TradingIndicatorStrategy.__abstractmethods__
    with pytest.raises(TypeError):
        TradingIndicatorStrategy()


def test_each_indicator_is_its_own_concrete_strategy():
    for cls in CONCRETE:
        assert issubclass(cls, TradingIndicatorStrategy), f"{cls.__name__} must subclass TradingIndicatorStrategy"
        assert not inspect.isabstract(cls), f"{cls.__name__} must implement calculate_indicator"


def test_moving_average():
    s = MovingAverageStrategy()
    assert s.calculate_indicator(Stock("ACME", 10.0, 20.0)) == 15.0, "(price + previous_close) / 2"
    assert s.calculate_indicator(Stock("ACME", 7.0, 7.0)) == 7.0


def test_momentum_keeps_its_sign():
    s = MomentumStrategy()
    assert s.calculate_indicator(Stock("ACME", 10.0, 20.0)) == -10.0, "price - previous_close, negative when falling"
    assert s.calculate_indicator(Stock("ACME", 25.0, 20.0)) == 5.0


def test_volatility_is_never_negative():
    s = VolatilityStrategy()
    assert s.calculate_indicator(Stock("ACME", 10.0, 20.0)) == 10.0, "abs(price - previous_close)"
    assert s.calculate_indicator(Stock("ACME", 20.0, 10.0)) == 10.0
    assert s.calculate_indicator(Stock("ACME", 5.0, 5.0)) == 0.0


def test_strategies_only_use_price_and_previous_close():
    stock = SimpleNamespace(price=10.0, previous_close=20.0)
    assert MovingAverageStrategy().calculate_indicator(stock) == 15.0
    assert MomentumStrategy().calculate_indicator(stock) == -10.0
    assert VolatilityStrategy().calculate_indicator(stock) == 10.0


def test_manager_delegates_once_with_the_same_stock():
    seen = []

    class Spy(TradingIndicatorStrategy):
        def calculate_indicator(self, stock):
            seen.append(stock)
            return 99.0

    stock = Stock("ACME", 1.0, 2.0)
    assert StockTradingManager(Spy()).calculate_indicator(stock) == 99.0, "return exactly what the strategy returns"
    assert len(seen) == 1 and seen[0] is stock, "delegate exactly once, passing the same stock"


def test_one_manager_class_serves_every_strategy_including_new_ones():
    class Spread(TradingIndicatorStrategy):
        def calculate_indicator(self, stock):
            return stock.price * 2

    stock = Stock("ACME", 10.0, 20.0)
    results = [StockTradingManager(s).calculate_indicator(stock)
               for s in (MovingAverageStrategy(), MomentumStrategy(), VolatilityStrategy(), Spread())]
    assert results == [15.0, -10.0, 10.0, 20.0], f"the manager must not branch on strategy kind; got {results}"
