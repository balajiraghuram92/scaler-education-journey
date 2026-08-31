package com.assignment.question;

public class MomentumStrategy implements TradingIndicatorStrategy {
    @Override
    public TradingStrategyType supportsType() {
        return TradingStrategyType.MOMENTUM;
    }

    @Override
    public Double calculateIndicator(Stock stock) {
        return stock.getPrice() - stock.getPreviousPrice();
    }
}
