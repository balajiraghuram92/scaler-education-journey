package com.assignment.question;

import com.assignment.question.notification.Notification;
import com.assignment.question.notification.PushNotification;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.sender.PushNotificationSender;
import com.assignment.question.template.NotificationTemplate;
import com.assignment.question.template.PushNotificationTemplate;

// TODO: extend NotificationFactory, wiring up the Push family: PushNotification,
// PushNotificationTemplate, PushNotificationSender.
public class PushNotificationFactory extends NotificationFactory {

    @Override
    public NotificationType notificationType() {
        return null;
    }

    @Override
    public Notification createNotification(String recipient, String sender, NotificationTemplate template) {
        return null;
    }

    @Override
    public NotificationTemplate createTemplate(String templateName) {
        return null;
    }

    @Override
    public NotificationSender createSender(Notification notification) {
        return null;
    }
}
