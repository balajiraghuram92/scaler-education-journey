package com.assignment.question.sender;

import com.assignment.question.NotificationType;
import com.assignment.question.notification.Notification;

// TODO: extend NotificationSender and implement send() and notificationType()
// (returning NotificationType.EMAIL).
public class EmailNotificationSender extends NotificationSender {

    public EmailNotificationSender(Notification notification) {
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
