# Introduction to Threads

Source folder: `1773391158_5666186fc2592b59/Introduction_to_-solution`

## Problem Statement

Lecture 5 Assignment 1 - Introduction to Threads. This exercise covers basic threading concepts in Java.

## Graded Contract (from tests)

From `ClientTest.java`, the following must be present and function correctly:

- **Class `Client`**
  - Must have a static `main(String[] args)` method (signature verified via reflection)
  - When main() is invoked, it must create and start two ScalerThread instances: one with Adder, one with Subtractor
  - Each thread name must be captured in `ScalerThread.map` (public static HashMap<String, String>)

- **Class `Adder`** (must exist; verified via `Class.forName("Adder")`)
  - Must implement `java.lang.Runnable` interface
  - Must have a `run()` method (from Runnable)
  - `run()` method must print "I am the Adder class\n" to stdout

- **Class `Subtractor`** (must exist; verified via `Class.forName("Subtractor")`)
  - Must implement `java.lang.Runnable` interface
  - Must have a `run()` method (from Runnable)
  - `run()` method must print "I am the Subtractor class\n" to stdout

- **Class `ScalerThread`**
  - Must extend `java.lang.Thread`
  - Must have a public static `HashMap<String, String> map` field
  - Must have a constructor that accepts a `Runnable` parameter
  - Must override `start()` method:
    - Call `super.start()`
    - Store the Runnable's class name as key and thread name as value in the map

## Learner Template

```java
public class Client {
    public static void main(String[] args) {
        // TODO: implement
    }
}
```

```java
public class Adder implements Runnable {
    @Override
    public void run() {
        // TODO: implement
    }
}
```

```java
public class Subtractor implements Runnable {
    @Override
    public void run() {
        // TODO: implement
    }
}
```

```java
import java.util.HashMap;

public class ScalerThread extends Thread {
    public static HashMap<String, String> map = new HashMap<>();
    
    public ScalerThread(Runnable r) {
        // TODO: implement
    }
    
    @Override
    public void start() {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field `target` in `ScalerThread` (to store Runnable class name)
- Constructor logic that extracts Runnable class name via reflection
- Implementation details of `start()` method's thread tracking logic
- Console output strings in Adder and Subtractor
- Main method logic (how to instantiate and start threads)
