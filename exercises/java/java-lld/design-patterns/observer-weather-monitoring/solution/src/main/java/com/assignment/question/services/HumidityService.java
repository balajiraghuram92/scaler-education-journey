package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class HumidityService implements Observer {
    @Override
    public void notifyObserver(double value) {
        NotificationUtils.sendNotification("New value is " + value);
    }
}
