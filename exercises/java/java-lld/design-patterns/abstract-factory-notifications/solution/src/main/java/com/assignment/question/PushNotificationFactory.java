package com.assignment.question;

import com.assignment.question.notification.Notification;
import com.assignment.question.notification.PushNotification;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.sender.PushNotificationSender;
import com.assignment.question.template.NotificationTemplate;
import com.assignment.question.template.PushNotificationTemplate;

public class PushNotificationFactory extends NotificationFactory {

    @Override
    public NotificationType notificationType() {
        return NotificationType.PUSH;
    }

    @Override
    public Notification createNotification(String recipient, String sender, NotificationTemplate template) {
        return new PushNotification(recipient, template);
    }

    @Override
    public NotificationTemplate createTemplate(String templateName) {
        return new PushNotificationTemplate(templateName);
    }

    @Override
    public NotificationSender createSender(Notification notification) {
        return new PushNotificationSender(notification);
    }
}
