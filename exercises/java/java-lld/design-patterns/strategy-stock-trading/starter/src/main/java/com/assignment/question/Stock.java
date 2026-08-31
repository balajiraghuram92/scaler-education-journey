package com.assignment.question;

public class Stock {
    private Double price;
    private Double previousPrice;

    public Stock(Double price, Double previousPrice) {
        this.price = price;
        this.previousPrice = previousPrice;
    }

    public Double getPrice() {
        return price;
    }

    public Double getPreviousPrice() {
        return previousPrice;
    }
}
