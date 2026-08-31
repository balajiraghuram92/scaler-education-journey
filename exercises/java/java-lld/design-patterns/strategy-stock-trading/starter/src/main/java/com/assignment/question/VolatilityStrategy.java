package com.assignment.question;

// TODO: implement TradingIndicatorStrategy — supportsType() returns VOLATILITY,
// calculateIndicator(...) returns the absolute difference between price and previousPrice.
public class VolatilityStrategy implements TradingIndicatorStrategy {
    @Override
    public TradingStrategyType supportsType() {
        return null;
    }

    @Override
    public Double calculateIndicator(Stock stock) {
        return null;
    }
}
