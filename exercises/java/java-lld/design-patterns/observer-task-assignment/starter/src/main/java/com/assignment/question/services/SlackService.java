package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

// TODO: implement Observer — notifyObserver(...) should call
// NotificationUtils.sendSlack("New task assigned", "Task <taskId> assigned to user <userId>").
public class SlackService implements Observer {
    @Override
    public void notifyObserver(Long taskId, Long userId) {

    }
}
