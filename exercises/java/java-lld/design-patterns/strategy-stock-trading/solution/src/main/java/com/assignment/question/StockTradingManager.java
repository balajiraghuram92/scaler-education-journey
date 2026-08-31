package com.assignment.question;

public class StockTradingManager {

    private TradingIndicatorStrategy indicatorStrategy;
    public StockTradingManager(TradingIndicatorStrategy indicatorStrategy) {
        this.indicatorStrategy = indicatorStrategy;
    }

    public Double calculateIndicator(Stock stock) {
        return indicatorStrategy.calculateIndicator(stock);
    }
}
