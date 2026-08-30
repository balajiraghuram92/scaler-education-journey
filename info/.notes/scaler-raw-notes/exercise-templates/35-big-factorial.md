# Big Factorial Thread

Source folder: 1773391702_ec4f115ebacdbb5b/Big_Factorial_-_-solution

## Problem Statement

Implement a thread that computes factorials of large numbers. Since the factorial result can be significantly large, you must use the `BigInteger` class to store the result and perform the computation. The class should extend the Thread class and override the `run()` method to perform factorial computation in a separate thread. The system must handle thread lifecycle correctly and provide access to the computed result through a getter method.

## Graded Contract (from tests)

- **BigFactorial class**: Must extend Thread
- **Constructor**: `BigFactorial(int number)` - accepts the number for factorial computation
- **run() method**: Must override to compute factorial using BigInteger
- **getFactorial() method**: Returns BigInteger representing the computed factorial
- Tests verify: correct computation for various values (0, 10, 20, 1000), thread state after execution (TERMINATED), ability to interrupt thread gracefully

## Learner Template

```java
package org.example;

import java.math.BigInteger;

public class BigFactorial extends Thread {
    // TODO: Declare private field for number
    // TODO: Declare field for factorial result
    
    public BigFactorial(int number) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void run() {
        // TODO: Call method to calculate factorial and store result
        throw new UnsupportedOperationException("TODO");
    }

    public BigInteger getFactorial() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field declarations (number, factorial)
- Constructor body for field initialization
- Private helper method `calculateFactorial(int n)` for computing factorial iteratively
- The loop logic for multiplying numbers to compute factorial
- BigInteger method calls (valueOf, multiply, ONE)
- Main method with thread creation and join() calls
- Exception handling for InterruptedException

