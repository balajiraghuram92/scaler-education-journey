package com.assignment.question;

import com.assignment.question.notification.EmailNotification;
import com.assignment.question.notification.Notification;
import com.assignment.question.sender.EmailNotificationSender;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.template.EmailNotificationTemplate;
import com.assignment.question.template.NotificationTemplate;

// TODO: extend NotificationFactory, wiring up the Email family: EmailNotification,
// EmailNotificationTemplate, EmailNotificationSender.
public class EmailNotificationFactory extends NotificationFactory {

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
