package com.assignment.question.sender;

import com.assignment.question.NotificationType;
import com.assignment.question.notification.Notification;

// TODO: extend NotificationSender and implement send() and notificationType()
// (returning NotificationType.PUSH).
public class PushNotificationSender extends NotificationSender {

    public PushNotificationSender(Notification notification) {
        super(notification);
    }

    @Override
    public void send() {

    }

    @Override
    public NotificationType notificationType() {
        return null;
    }
}
