# Builder Pattern Implementation for a Messaging Service

Source folder: `1773391243_8a1045a69c65b34f/Builder_Message-solution`

## Problem Statement

You are developing a messaging application with support for various message types, including text, images, audio, and video. Each message type can have additional attributes and settings, such as delivery status and timestamps. The current approach of creating message objects using multiple overloaded constructors has become error-prone and challenging to maintain. You should streamline the creation of message objects with different configurations and immutable objects.

Your task is to implement the Builder pattern to create instances of message objects with different configurations. The Builder pattern allows for step-by-step construction of complex objects while keeping the creation process separate from the main object.

## Graded Contract (from tests)

- **Class `Message`** (reference/original class)
  - Fields: `messageType` (MessageType), `content` (String), `sender` (String), `recipient` (String), `isDelivered` (boolean), `timestamp` (long)
  - Constructor and getters for all fields

- **Enum `MessageType`**
  - Values: `TEXT`, `IMAGE`, `AUDIO`, `VIDEO`

- **Annotation `@WithBuilder`**
  - Marks the builder implementation class
  - Must be exactly one class in the package annotated with this

- **Builder outer class** (annotated with `@WithBuilder`)
  - Must have all fields from Message with matching names and types
  - Must have a public no-args constructor
  - Static inner class `Builder` that is public and static

- **Static inner class `Builder`**
  - Constructor: `public Builder()` — no-args constructor
  - Must either:
    - Have fields matching all Message fields, OR
    - Have a field that references the outer builder class instance
  - Method: `build()` — returns instance of outer class with all field values copied
  - Builder methods (messageType, content, sender, recipient, isDelivered, timestamp) for fluent API

- **Test contract details**
  - Tests use reflection to find `@WithBuilder` annotated class
  - Tests check that all fields from Message exist in the builder
  - Tests verify Builder inner class copies values correctly

## Learner Template

```java
package com.assignment.question;

public enum MessageType {
    TEXT,
    IMAGE,
    AUDIO,
    VIDEO
}
```

```java
package com.assignment.question;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface WithBuilder {
}
```

```java
package com.assignment.question;

@WithBuilder
public class MessageBuilder {
    private MessageType messageType;
    private String content;
    private String sender;
    private String recipient;
    private boolean isDelivered;
    private long timestamp;

    public MessageBuilder() {
        // TODO: implement
    }

    public static Builder builder() {
        // TODO: implement - return new Builder instance
    }

    public static class Builder {
        private MessageBuilder messageBuilder;

        public Builder() {
            // TODO: implement
        }

        public Builder messageType(MessageType messageType) {
            // TODO: implement
        }

        public Builder content(String content) {
            // TODO: implement
        }

        public Builder sender(String sender) {
            // TODO: implement
        }

        public Builder recipient(String recipient) {
            // TODO: implement
        }

        public Builder isDelivered(boolean isDelivered) {
            // TODO: implement
        }

        public Builder timestamp(long timestamp) {
            // TODO: implement
        }

        public MessageBuilder build() {
            // TODO: implement - create new outer instance with field values
        }
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field initialization and persistence logic in MessageBuilder
- Builder method implementations (chaining logic via returning `this`)
- Build method instantiation and field copying logic
- Whether to use an internal reference to MessageBuilder in Builder or duplicate fields
- Getter methods (not required by contract)
