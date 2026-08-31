package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

public abstract class Publisher implements ObserverRegistry {

    private List<Observer> observers = new ArrayList<>();

    @Override
    public void addObserver(Observer observer) {
        observers.add(observer);
    }
    @Override
    public void removeObserver(Observer observer) {
        observers.remove(observer);
    }

    @Override
    public void notifyObservers(String stockName, double currentPrice) {
        observers.forEach(observer -> observer.notifyObserver(stockName, currentPrice));
    }
}
