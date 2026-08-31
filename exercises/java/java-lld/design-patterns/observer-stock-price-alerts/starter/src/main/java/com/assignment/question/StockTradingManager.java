package com.assignment.question;

// TODO: extend Publisher. updateStockPrice(...) should update the current price and,
// if it exceeds notificationThreshold, notify all registered observers with the
// stock name and the new price.
public class StockTradingManager extends Publisher {

    private String stockName;
    private double currentPrice;
    private double notificationThreshold;

    public StockTradingManager(String stockName, double initialPrice, double notificationThreshold) {
        this.stockName = stockName;
        this.currentPrice = initialPrice;
        this.notificationThreshold = notificationThreshold;
    }

    public void updateStockPrice(double newPrice) {

    }

}
