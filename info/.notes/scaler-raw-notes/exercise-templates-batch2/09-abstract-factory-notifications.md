# Abstract Factory Pattern for Notifications

Source folder: `1773391281_ef347fcfc6fd514d/Abstract_Factory-solution`

## Problem Statement

You are working on a notification system for a communication application. The application must support different types of notifications, such as email, SMS, and push notifications. Each notification type has specific content and delivery methods. You want to design a flexible notification system where different types of notifications can be created without specifying their concrete classes, ensuring the system is open for future notification types and supports compatibility within families.

## Detailed Requirements

Your task is to implement the Abstract Factory pattern to create notifications and related components in the communication application. The Abstract Factory pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes, allowing for easy addition of new notification types and ensuring compatibility within families.

### Task 1 - Defining the Abstract Factory

The abstract factory class has been created for you. You will need to add the factory methods to create the notification, templates, and senders to the abstract factory class. The method `notificationType` has already been abstracted out for you as an example. You will need to implement the `NotificationFactory` class as a common parent class for all the notification factories.

### Task 2 - Implementing Concrete Factories

Create concrete implementations of the `NotificationFactory` interface for email and push notifications. Implement the methods to create compatible notifications, notification providers, and notification templates for each notification type. Ensure that the created components are compatible within the same family.

### Task 3 - Testing the Implementation

Run the provided test cases in the `NotificationFactoryTest` class to verify the correctness of your implementation. The tests will check if all notifications have a common parent class, and if the factory classes can correctly create notifications, notification providers, and notification templates based on the notification type and content.

### Instructions

1. Implement the `NotificationFactory` interface with methods to create notifications, notification providers, and notification templates.
2. Create concrete implementations of the `NotificationFactory` interface for email, SMS, and push notifications. Implement the methods to create compatible components for each notification type.
3. Run the provided test cases in the `NotificationFactoryTest` class to verify the correctness of your implementation. The tests will ensure that the factory classes can correctly create notification components based on the notification type and content.

## Graded Contract (from tests)

- **NotificationFactory abstract parent class:** Must exist as abstract class
- **NotificationFactory methods (all abstract):**
  - `notificationType()` - returns `NotificationType`, no parameters
  - `createNotification(String recipient, String sender, NotificationTemplate template)` - returns `Notification`
  - `createTemplate(String templateName)` - returns `NotificationTemplate`
  - `createSender(Notification notification)` - returns `NotificationSender`
- **Number of concrete factories:** Exactly 2 implementations (EmailNotificationFactory, PushNotificationFactory)
- **Notification abstract class:** Must exist with `notificationType()` and `sendNotification()` abstract methods
- **NotificationTemplate abstract class:** Must exist with `notificationType()` method
- **NotificationSender abstract class:** Must exist with `notificationType()` method
- **Concrete implementations:** Must correctly implement all abstract methods and return appropriate type-specific components

## Learner Template

```java
// NotificationFactory.java - Abstract Factory
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
```

```java
// EmailNotificationFactory.java - Concrete Factory
package com.assignment.question;

import com.assignment.question.notification.Notification;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.template.NotificationTemplate;

public class EmailNotificationFactory extends NotificationFactory {
    
    @Override
    public NotificationType notificationType() {
        // TODO: implement
    }
    
    @Override
    public Notification createNotification(String recipient, String sender, NotificationTemplate template) {
        // TODO: implement
    }
    
    @Override
    public NotificationTemplate createTemplate(String templateName) {
        // TODO: implement
    }
    
    @Override
    public NotificationSender createSender(Notification notification) {
        // TODO: implement
    }
}
```

```java
// PushNotificationFactory.java - Concrete Factory
package com.assignment.question;

import com.assignment.question.notification.Notification;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.template.NotificationTemplate;

public class PushNotificationFactory extends NotificationFactory {
    
    @Override
    public NotificationType notificationType() {
        // TODO: implement
    }
    
    @Override
    public Notification createNotification(String recipient, String sender, NotificationTemplate template) {
        // TODO: implement
    }
    
    @Override
    public NotificationTemplate createTemplate(String templateName) {
        // TODO: implement
    }
    
    @Override
    public NotificationSender createSender(Notification notification) {
        // TODO: implement
    }
}
```

```java
// Notification.java - Abstract parent (reference)
package com.assignment.question.notification;

import com.assignment.question.NotificationType;
import com.assignment.question.template.NotificationTemplate;

public abstract class Notification {
    private String recipient;
    private NotificationTemplate template;

    public Notification(String recipient, NotificationTemplate template) {
        this.recipient = recipient;
        this.template = template;
    }

    public String getRecipient() {
        return recipient;
    }

    public NotificationTemplate getTemplate() {
        return template;
    }

    public abstract NotificationType notificationType();
    public abstract void sendNotification();
}
```

```java
// NotificationType.java - Enumeration
package com.assignment.question;

public enum NotificationType {
    EMAIL, SMS, PUSH
}
```

## Deliberately Left Out (for the learner to design)

- Concrete implementations of EmailNotification and PushNotification classes
- Concrete implementations of EmailNotificationTemplate and PushNotificationTemplate classes
- Concrete implementations of EmailNotificationSender and PushNotificationSender classes
- Implementation logic for all abstract methods in concrete factories
- Implementation logic for sendNotification() in concrete notification classes
- NotificationTemplate and NotificationSender abstract parent classes (may need to create)
