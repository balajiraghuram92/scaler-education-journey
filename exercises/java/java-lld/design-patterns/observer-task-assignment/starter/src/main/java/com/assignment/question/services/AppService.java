package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

// TODO: implement Observer — notifyObserver(...) should call
// NotificationUtils.sendPush("New task assigned", "Task <taskId> assigned to user <userId>").
public class AppService implements Observer {
    @Override
    public void notifyObserver(Long taskId, Long userId) {

    }
}
