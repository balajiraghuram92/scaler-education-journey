package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class AppService implements Observer {
    @Override
    public void notifyObserver(Long taskId, Long userId) {
        String subject = "New task assigned";
        String message = "Task %s assigned to user %s";
        NotificationUtils.sendPush(subject, String.format(message, taskId, userId));
    }
}
