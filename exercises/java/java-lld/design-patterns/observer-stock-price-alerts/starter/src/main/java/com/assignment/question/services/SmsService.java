package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

// TODO: implement Observer — notifyObserver(...) should call
// NotificationUtils.sendSms("Price update for <stockName>", "New price is <currentPrice>").
public class SmsService implements Observer {
    @Override
    public void notifyObserver(String stockName, double currentPrice) {

    }
}
