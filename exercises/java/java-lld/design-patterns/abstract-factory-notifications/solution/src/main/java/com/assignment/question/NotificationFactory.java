package com.assignment.question;

import com.assignment.question.notification.Notification;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.template.NotificationTemplate;

public abstract class NotificationFactory {

    public abstract NotificationType notificationType();

    public abstract Notification createNotification(String recipient, String sender, NotificationTemplate template);
    public abstract NotificationTemplate createTemplate(String templateName);
    public abstract NotificationSender createSender(Notification notification);

}
