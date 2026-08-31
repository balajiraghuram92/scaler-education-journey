package com.assignment.question;

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
        currentPrice = newPrice;
        if (currentPrice > notificationThreshold) {
            notifyObservers(stockName, currentPrice);
        }
    }

}
