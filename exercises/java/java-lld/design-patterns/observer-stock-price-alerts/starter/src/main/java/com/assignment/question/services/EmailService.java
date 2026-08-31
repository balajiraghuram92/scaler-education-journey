package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

// TODO: implement Observer — notifyObserver(...) should call
// NotificationUtils.sendEmail("Price update for <stockName>", "New price is <currentPrice>").
public class EmailService implements Observer {
    @Override
    public void notifyObserver(String stockName, double currentPrice) {

    }
}
