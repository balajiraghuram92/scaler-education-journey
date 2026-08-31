package com.assignment.question.notification;

import com.assignment.question.NotificationType;
import com.assignment.question.template.NotificationTemplate;

// TODO: extend Notification, storing a sender field, and implement
// sendNotification() and notificationType() (returning NotificationType.EMAIL).
public class EmailNotification extends Notification {

    public EmailNotification(String recipient, String sender, NotificationTemplate template) {
        super(recipient, template);
    }

    @Override
    public void sendNotification() {

    }

    @Override
    public NotificationType notificationType() {
        return null;
    }
}
