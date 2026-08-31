package com.assignment.question.notification;

import com.assignment.question.NotificationType;
import com.assignment.question.template.NotificationTemplate;

// TODO: extend Notification and implement sendNotification() and
// notificationType() (returning NotificationType.PUSH).
public class PushNotification extends Notification {

    public PushNotification(String recipient, NotificationTemplate template) {
        super(recipient, template);
    }

    @Override
    public void sendNotification() {

    }

    public NotificationType notificationType() {
        return null;
    }
}
