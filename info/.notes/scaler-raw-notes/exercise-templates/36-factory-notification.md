# Factory Notification System

Source folder: 1786432647_f9e1b9844feac804/Factory_Notifica-solution

## Problem Statement

You are designing a notification system using the Simple Factory pattern. Depending on the type of notification (email, SMS, or push), different notification routines are required. You need a way to create notifications without explicitly specifying their classes, ensuring the system is open for future notification types. Implement a Notification abstract superclass that serves as a common parent for all notification types, and a NotificationFactory class that creates appropriate notification instances based on type.

## Graded Contract (from tests)

- **NotificationType enum**: Must have three values: EMAIL, PUSH, SMS
- **Notification abstract class**: Must have 2 private String fields (recipient, message); methods `getRecipient()` and `getMessage()` returning String; abstract methods `notificationType()` returning NotificationType and `sendNotification()` returning void
- **EmailNotification class**: Extends Notification; constructor `(String recipient, String sender, String message)`
- **SmsNotification class**: Extends Notification; constructor `(String recipient, String message)`
- **PushNotification class**: Extends Notification; constructor `(String recipient, String message)`
- **NotificationFactory class**: Has static method `createNotification(NotificationType notificationType, String recipient, String message, String sender)` that returns Notification; must handle all three notification types
- Tests verify: exactly 3 subclasses of Notification, factory creates correct type instances

## Learner Template

```java
package com.assignment.question;

public enum NotificationType {
    // TODO: implement
    throw new UnsupportedOperationException("TODO");
}
```

```java
package com.assignment.question;

public abstract class Notification {
    // TODO: Declare private String fields for recipient and message
    
    public Notification(String recipient, String message) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getRecipient() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getMessage() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public abstract NotificationType notificationType();

    public abstract void sendNotification();
}
```

```java
package com.assignment.question;

public class EmailNotification extends Notification {
    // TODO: Declare private field for sender
    
    public EmailNotification(String recipient, String sender, String message) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getSender() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void sendNotification() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public NotificationType notificationType() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package com.assignment.question;

public class SmsNotification extends Notification {
    public SmsNotification(String recipient, String message) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void sendNotification() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public NotificationType notificationType() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package com.assignment.question;

public class PushNotification extends Notification {
    public PushNotification(String recipient, String message) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void sendNotification() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public NotificationType notificationType() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package com.assignment.question;

public class NotificationFactory {
    public static Notification createNotification(NotificationType notificationType, String recipient, String message, String sender) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Enum value definitions (EMAIL, PUSH, SMS)
- Private field declarations in Notification and EmailNotification
- Constructor bodies for all classes with field initialization and super() calls
- Getter implementations
- Implementation of `sendNotification()` for each notification type (print statements)
- Implementation of `notificationType()` for each notification type (return enum value)
- Switch/if-else logic in factory to create correct notification type
- Exception handling for invalid notification types
- Main method if any

