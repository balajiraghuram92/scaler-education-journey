package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

// TODO: implement the Observer pattern's registry — addObserver adds to the list,
// removeObserver removes from it, notifyObservers calls notifyObserver(taskId, userId)
// on every registered observer.
public abstract class Publisher {

    private List<Observer> observers = new ArrayList<>();

    public void addObserver(Observer observer) {

    }

    public void removeObserver(Observer observer) {

    }

    protected void notifyObservers(Long taskId, Long userId) {

    }
}
