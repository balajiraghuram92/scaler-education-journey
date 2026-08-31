package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

public abstract class Publisher {

    private List<Observer> observers = new ArrayList<>();

    public void addObserver(Observer observer) {
        observers.add(observer);
    }

    public void removeObserver(Observer observer) {
        observers.remove(observer);
    }

    protected void notifyObservers(Long taskId, Long userId) {
        observers.forEach(observer -> observer.notifyObserver(taskId, userId));
    }
}
