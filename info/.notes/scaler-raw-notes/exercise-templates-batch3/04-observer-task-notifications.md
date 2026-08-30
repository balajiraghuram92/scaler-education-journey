# Observer Pattern for Task Management Application

Source folder: `1773391221_ba5246debdca20e7/Task_Observer-solution`

## Problem Statement

You are building a task management application where users can create tasks and assign them to different team members. To enhance the user experience, Joe, a developer on your team, wants to implement a feature where team members receive notifications whenever they are assigned a new task. These notifications should be sent through various communication channels, such as in-app alerts, emails, and Slack messages. Joe believes that implementing the Observer pattern will provide a flexible and maintainable solution for this requirement.

## Detailed Requirements

1. **Understand the original class**: Take a closer look at the `TaskManager` class and its interactions with the task database and notification services. Understand how tasks are assigned and notifications are sent.

2. **Implement the observer interface**: Implement the interface named `Observer` with a method that accepts the task and the team member as arguments. Observer classes (such as `AlertService`, `EmailService`, `SlackService`) will implement this interface to receive notifications.

3. **Implement the publisher interface**: You have been provided with a `Publisher` abstract class. Your task is to implement the methods required by this interface in the `TaskManager` class. The `Publisher` interface defines methods that allow observers to subscribe and unsubscribe.

4. **Modify the observers**: Refactor the observer classes to implement the `Observer` interface. Update their existing methods to match the new interface method signature.

5. **Modify the publisher**: Refactor the `TaskManager` class as required. Implement the publisher methods to manage observer subscriptions and notify observers when a task is assigned.

6. **Test your implementation**: Run the provided test cases in the `TaskManagerTest` class to ensure that your observer pattern implementation is correct. These test cases will check if observers are being notified correctly and if the `TaskManager` behaves as expected.

## Graded Contract (from tests)

- TaskManager must **not have any fields** of type `EmailService`, `SlackService`, or `AppService` (loose coupling requirement)
- `Observer` interface must declare exactly **one method with two parameters of type `Long`** (taskId and userId)
- `Publisher` class must declare **at least two methods taking a single `Observer` parameter** (for add and remove)
- `TaskManager` must have a **default (no-arg) constructor**
- `TaskManager` must **extend `Publisher`**
- `EmailService`, `SlackService`, and `AppService` must each **implement `Observer`**
- When `TaskManager.assignTask(Long taskId, Long userId)` is called:
  - All registered observers' `notifyObserver(Long taskId, Long userId)` method must be invoked
  - Observers must receive correct taskId and userId values
  - `NotificationUtils.sendEmail()`, `NotificationUtils.sendSlack()`, and `NotificationUtils.sendPush()` must be called with the correct message format: `"New task assigned"` and `"Task <taskId> assigned to user <userId>"`

## Learner Template

```java
// Observer.java
package com.assignment.question;

public interface Observer {
    // TODO: Implement the observer notification method
    // Should accept two Long parameters: taskId and userId
}
```

```java
// Publisher.java
package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

public abstract class Publisher {
    private List<Observer> observers = new ArrayList<>();

    // TODO: Implement method to add an observer
    
    // TODO: Implement method to remove an observer
    
    // TODO: Implement method to notify all observers
    // Should invoke notifyObserver() on each observer with taskId and userId
}
```

```java
// TaskManager.java
package com.assignment.question;

public class TaskManager extends Publisher {
    // TODO: Implement constructor (if needed)
    
    // TODO: Implement assignTask method
    // Should notify observers when a task is assigned
}
```

```java
// AppService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class AppService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendPush() with subject "New task assigned"
    // and message "Task <taskId> assigned to user <userId>"
}
```

```java
// EmailService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class EmailService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendEmail() with subject "New task assigned"
    // and message "Task <taskId> assigned to user <userId>"
}
```

```java
// SlackService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class SlackService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendSlack() with subject "New task assigned"
    // and message "Task <taskId> assigned to user <userId>"
}
```

## Deliberately Left Out (for the learner to design)

- The exact method signature of `notifyObserver()` in the `Observer` interface
- The implementation of `addObserver()`, `removeObserver()`, and `notifyObservers()` in `Publisher`
- The implementation of `TaskManager.assignTask()` and how it uses the Publisher methods
- The implementation of each service's `notifyObserver()` method and the exact message format
- The internal `observers` list management in `Publisher`
