package com.assignment.question.template;

import com.assignment.question.NotificationType;

// TODO: extend NotificationTemplate and implement applyTemplate() and
// notificationType() (returning NotificationType.PUSH).
public class PushNotificationTemplate extends NotificationTemplate {
    public PushNotificationTemplate(String message) {
        super(message);
    }

    @Override
    public String applyTemplate() {
        return null;
    }

    @Override
    public NotificationType notificationType() {
        return null;
    }
}
