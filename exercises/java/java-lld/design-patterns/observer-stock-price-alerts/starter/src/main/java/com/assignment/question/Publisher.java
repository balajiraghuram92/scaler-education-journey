package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

// TODO: implement ObserverRegistry — addObserver adds to the list, removeObserver
// removes from it, notifyObservers calls notifyObserver(stockName, currentPrice)
// on every registered observer.
public abstract class Publisher implements ObserverRegistry {

    private List<Observer> observers = new ArrayList<>();

    @Override
    public void addObserver(Observer observer) {

    }

    @Override
    public void removeObserver(Observer observer) {

    }

    @Override
    public void notifyObservers(String stockName, double currentPrice) {

    }
}
