Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/ByFK0-FQMl

# Post-Read_Concurrency3 Study Guide

## Overview
This document consolidates a Concurrency-3 session covering synchronization fundamentals in Java. The material progresses from identifying shared memory problems through three solution approaches: explicit locks, synchronized blocks, and synchronized methods.

## Core Problem: The Broken Counter

The document illustrates unsafe shared memory through a simple example: one shared counter, two threads (Adder and Subtractor) performing opposite operations 100 times each. Mathematically, the result should be zero, but execution produces unpredictable values like 4, -7, or 12.

As stated: "Separate memory = safe. Shared memory = danger."

## Three Key Concepts

**Critical Section**: "any code that reads or writes shared, mutable data"

**Race Condition**: The outcome depends on thread execution timing rather than logic

**Pre-emption**: The scheduler switching threads mid-task without permission, enabling races

## Three Solution Approaches

1. **Mutex/Lock**: Explicit `ReentrantLock` with manual `lock()` and `unlock()` calls
2. **Synchronized Block**: `synchronized (objectName) { criticalCode }` 
3. **Synchronized Method**: `synchronized returnType methodName()` locks the calling object

## The Lock Ownership Rule

"The lock is on the OBJECT. Not on the method. Not on the thread."

This means:
- Same object + synchronized methods = same lock, sequential execution
- Same object + one synchronized + one unsynchronized = unsynchronized runs freely
- Different objects = independent locks, concurrent execution

## Producer-Consumer Pattern

Multiple producers add items to a bounded store; multiple consumers remove them. The naive implementation crashes with `IndexOutOfBoundsException` when multiple threads execute a "check-then-act" pattern simultaneously, each seeing room/items before any complete their action.

Wrapping checks in `synchronized (store)` prevents crashes but creates inefficiency: only one thread accesses the store at a time, even when multiple threads could safely proceed.

## Key Limitation

"synchronized's all-or-nothing nature"—it cannot express admitting N threads based on actual capacity. This limitation sets up the next session's topic: Semaphores, which provide counting-based mutual exclusion.
