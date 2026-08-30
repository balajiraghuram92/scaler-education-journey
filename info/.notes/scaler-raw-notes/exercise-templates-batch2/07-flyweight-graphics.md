# Flyweight Pattern for Graphics Elements

Source folder: `1773391261_cec30e8b32f48f4d/Flyweight_Graphi-solution`

## Problem Statement

You are working on a graphical editing software. The application must support rendering text with different fonts, sizes, and colors. The application must also support rendering images with different dimensions and formats. Joe is concerned about the memory overhead of creating multiple text and image objects with the same state.

## Detailed Requirements

Your task is to implement the Flyweight pattern to optimize the memory usage of graphical elements in the editing software. The Flyweight pattern aims to share common state between multiple objects to reduce memory consumption.

### Task 1 - Intrinsic and Extrinsic State Separation

In the Flyweight pattern, objects are split into intrinsic state (shared and independent of the context) and extrinsic state (variable and dependent on the context). Your task is to refactor the initial `Graphic` class into two separate classes: `GraphicIntrinsicState` and `GraphicExtrinsicState`.

**GraphicIntrinsicState class:**
- Create a class named `GraphicIntrinsicState` with appropriate fields to represent the intrinsic state of a graphic element.
- Annotate this class with the `@IntrinsicState` annotation.

**GraphicExtrinsicState class:**
- Create a class named `GraphicExtrinsicState` with appropriate fields to represent the extrinsic state of a graphic element.
- Annotate this class with the `@ExtrinsicState` annotation.

### Task 2 - Implementing the registry pattern

To make the storage and usability of the flyweight easier, implement the registry pattern:
- Create a registry class to implement the interface `FlyweightRegistry`.
- The class should store the flyweight and fetch the relevant flyweight based on the type.

### Instructions

1. Implement the `GraphicIntrinsicState` and `GraphicExtrinsicState` by breaking the original class into intrinsic and extrinsic state.
2. Ensure that both classes are annotated with the appropriate annotations i.e. `@IntrinsicState` and `@ExtrinsicState`.
3. Implement the registry interface's `FlyweightRegistry` add and get flyweight methods.
4. Run the provided test cases in the `GraphicTest` class to verify the correctness of your implementation.

## Any Given "Before" Code

The original `Graphic` class would have fields that need to be separated into intrinsic (immutable, shared) and extrinsic (mutable, context-dependent) states.

Intrinsic fields (same across renderings): image, width, height, color
Extrinsic fields (vary per rendering): x, y

## Graded Contract (from tests)

- **@IntrinsicState annotation:** Exactly one class must be annotated with `@IntrinsicState`
- **GraphicIntrinsicState fields:** Must contain fields: `image`, `width`, `height`, `color`
- **@ExtrinsicState annotation:** Exactly one class must be annotated with `@ExtrinsicState`
- **GraphicExtrinsicState fields:** Must contain fields: `x`, `y`
- **ExtrinsicState reference field:** GraphicExtrinsicState must have a field of type GraphicIntrinsicState
- **FlyweightRegistry implementation:** Must be a concrete class implementing `FlyweightRegistry` interface
- **Registry storage:** FlyweightRegistry implementation must have a `Map` field for storing/fetching flyweights

## Learner Template

```java
// GraphicIntrinsicState.java
package com.assignment.question;

import lombok.Getter;

@IntrinsicState
@Getter
public class GraphicIntrinsicState {
    private Image image;
    private int width;
    private int height;
    private String color;
    private GraphicType type;
}
```

```java
// GraphicExtrinsicState.java
package com.assignment.question;

@ExtrinsicState
public class GraphicExtrinsicState {
    private int x;
    private int y;
    private GraphicIntrinsicState intrinsicState;
}
```

```java
// FlyweightRegistry interface (already provided)
package com.assignment.question;

public interface FlyweightRegistry {
    void addFlyweight(GraphicIntrinsicState flyweight);
    GraphicIntrinsicState getFlyweight(String type);
}
```

```java
// FlyweightRegistryImpl.java - Learner must implement this
package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

public class FlyweightRegistryImpl implements FlyweightRegistry {
    private Map<String, GraphicIntrinsicState> registry = new HashMap<>();

    @Override
    public void addFlyweight(GraphicIntrinsicState flyweight) {
        // TODO: implement
    }

    @Override
    public GraphicIntrinsicState getFlyweight(String type) {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Implementation logic in `FlyweightRegistryImpl.addFlyweight()` and `getFlyweight()` methods
- Any getter/setter methods for GraphicExtrinsicState fields (learners may add as needed)
- Getters for GraphicIntrinsicState fields (already provided via Lombok `@Getter`)
- Image and GraphicType supporting classes (assumed to be provided)
