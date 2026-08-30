Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/SklYF0bYmfg

# Lecture 8: PRE-READ - Concurrency-3 Introduction to Synchronization

## Overview

This session addresses what happens when multiple threads access shared memory simultaneously. The core progression moves from demonstrating a broken counter through three repair strategies.

| Block | Topic | Key Concepts |
|-------|-------|--------------|
| 1 | Shared data failure | Adder-Subtractor counter, read-modify-write operations |
| 2 | Problem terminology | Critical Section, Race Condition, Pre-emption |
| 3 | Solution 1 | Mutex, `Lock`, `ReentrantLock` with lock()/unlock() |
| 4 | Solution 2 | `synchronized` block construct |
| 5 | Solution 3 | `synchronized` method |
| 6 | Object-level locking | Lock attaches to object, not method |
| 7 | Complex scenario | Producer-Consumer with check-then-act bug |

## Why This Matters

Previous multithreaded exercises maintained complete data separation. Real systems—banking platforms, ticketing systems, inventory management—involve shared mutable data requiring explicit safety mechanisms.

The central principle: **"Separate memory is safe. Shared memory is danger."**

## Key Insight

A seemingly simple operation like `counter.setVal(counter.getVal() + i)` actually comprises three discrete steps: read, modify, write. Thread scheduling can interrupt between any step, creating race conditions where outcomes depend on unpredictable timing.

## Real-World Applications

**Critical Section in Banking**: Balance updates reading current value, adding deposits, and writing results back represent vulnerable code sections.

**Race Condition in Ticketing**: Multiple simultaneous seat-booking attempts create unpredictable outcomes when both threads read "available" before either claims it.

**Pre-emption**: The scheduler interrupts tasks between read-add-write steps, creating vulnerability windows.

**Mutex/Lock**: Single-key access where exactly one thread proceeds while others queue.

**Synchronized Methods**: Objects protect their own data across all thread callers.

**Producer-Consumer**: Multiple writers and readers access one shared storage, mirroring counter problems at scale.

## Prerequisites

Assumes working knowledge of:
- `ExecutorService`, `submit()`, `Future` from Concurrency-2
- `Callable` versus `Runnable` distinction
- Why merge sort avoided conflicts (separate memory sections)
- Task-based thinking patterns

## Foundational Rule

**"The lock is on the object. Not on the method. Not on the thread."**

Two threads calling different `synchronized` methods on the *same* object still cannot execute simultaneously—they compete for that object's single lock. Two threads calling the same method on *different* objects run independently with separate locks.

## Learning Outcomes

Upon completion, you will:

- Explain why single-line operations decompose into three discrete steps
- Define and identify Critical Section, Race Condition, and Pre-emption
- Use explicit `Lock`/`ReentrantLock` with proper `finally` block placement
- Apply `synchronized` block protection with correct object specification
- Implement `synchronized` methods understanding implicit object locking
- Predict thread execution patterns across synchronized method pairs
- Identify and fix check-then-act bugs in Producer-Consumer systems
- Articulate correctness versus efficiency tradeoffs in synchronization

## Environment Requirements

- JDK 17 or later (existing installation)
- IDE supporting Java execution (IntelliJ IDEA or VS Code with Java Extension Pack)
- Ability to run `main` methods multiple times observing different outputs
- `java.util.concurrent.locks` package (included in standard JDK)
- No external dependencies required

## Connection Forward

Today's conclusion—"can we allow N threads instead of exactly one?"—launches directly into the next session on Semaphores. The vocabulary (critical section, race condition, object-level locking) carries forward unchanged, building toward efficient multi-thread coordination without sacrificing correctness.
