Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/Sygxrx9j7fx

# Pre-Reads-Concurrency-4.md - HackMD

---

**title:** Pre-Reads
**tags:** [Final]

---

| PRE-READ | Concurrency and Synchronization | Concurrency-4 — Synchronization with Semaphores |
|----------|----------------------------------|--------------------------------------------------|

## Context

In the previous session, a race condition inside a shared Producer-Consumer store was resolved using a `synchronized` block. The fix was correct — the crash disappeared — but it came with a cost that was left open at the end of the class: `synchronized` permits exactly one thread inside the protected section at any time, regardless of how much capacity the shared resource actually has. Eight producer threads and twenty consumer threads were created, yet at any given instant only one of them was ever doing real work. Four empty shelves sat unused while three producers waited outside a locked door built for one. `synchronized` is a binary tool: a thread either holds the lock, or it does not. There is no way to instruct it to admit a specific number of threads at once. This session introduces the construct built specifically to solve that problem — one that can count.

## Overview

| Segment | What is covered | Concepts in play |
|---------|------------------|-------------------|
| Recap and the unresolved bottleneck | Why `synchronized` traded correctness for throughput | Binary access, the cost of "one at a time" |
| The Semaphore | A synchronization primitive that tracks a count of available permits | `Semaphore`, `permit`, `acquire()`, `release()` |
| Binary vs. counting semaphores | Why a semaphore with one permit behaves like a mutex, and why that generalizes | Binary semaphore, counting semaphore |
| Producer-Consumer, rebuilt | Replacing a single lock with two semaphores that signal each other | Cross-thread signalling, capacity vs. mutation |
| The bounded buffer pattern | Why a semaphore alone is not sufficient once multiple threads mutate shared state | Semaphore for capacity, mutex for mutation |
| Semaphore vs. mutex | The one structural difference that defines what each tool can and cannot do | Ownership |

This is the final session of the concurrency module. Everything covered builds directly on the previous three lectures and is intended to complete the reasoning toolkit for writing correct, efficient multithreaded code.

## Why This Session Matters

A `synchronized` block or a single `Lock` answers only one question: is a resource free, or is it not. Many real systems need a more precise answer: exactly how much of a shared resource is free right now, and can more than one thread act on it safely at the same time. A connection pool with ten connections, a rate limiter permitting a fixed number of requests per second, and a bounded queue between producers and consumers are all instances of this same underlying problem. A semaphore is the standard tool for reasoning about and implementing each of them. This is also material that surfaces directly in machine coding and system design interviews. A candidate who defaults to `synchronized` for every shared-resource problem, even when the problem explicitly calls for controlled concurrent access, is typically marked down. Recognizing when a counting construct is required — and being able to justify why a plain lock would either under-perform or under-constrain the problem — is a distinguishing signal.

## Real-World Use Cases

- **Semaphore as a counter:** A connection pool that allows at most ten simultaneous database connections is a semaphore initialized with ten permits. Every checkout is an `acquire()`; every return is a `release()`.

- **Semaphore as a signal between threads:** In a Producer-Consumer system, a producer does not merely add an item — it also communicates that an item is now available. A semaphore's `release()` call, issued by one thread and consumed by an entirely different thread, is what makes that communication possible without the two threads ever referencing each other directly.

- **Semaphore for grouping:** Some systems must wait until a fixed number of independent events have occurred before proceeding — assembling a batch, waiting for a fixed number of parallel sub-tasks to complete. `acquire(n)` expresses that requirement directly.

- **Bounded buffer:** Almost every real producer-consumer system — a message queue, a job scheduler, a logging pipeline with a fixed-size buffer — combines a semaphore (to track available capacity) with a mutex (to protect the shared data structure itself). This session builds that exact combination from first principles.

## Key Concept Preview

The formal definition to walk in holding:

> A **semaphore** is a synchronization construct that maintains an internal count of available **permits** and exposes two atomic operations: `acquire()`, which decrements the count and blocks the calling thread if no permit is available, and `release()`, which increments the count and unblocks a waiting thread if one exists.

A single distinction is worth previewing, because the entire second half of the session is built on it:

> A **mutex has an owner** — only the thread that acquired it may release it. A **semaphore has no owner** — any thread may call `release()`, whether or not it ever called `acquire()`.

This absence of ownership is simultaneously the reason a semaphore can be used for cross-thread signalling (a strength `synchronized` does not have) and the reason it can silently be misused (a safeguard `synchronized` does have). Both sides of that trade-off are covered in detail during the session.

## Connection to Prior Material

This session assumes the following from Lecture 3 (Synchronization with Mutexes):

- **Race condition and critical section:** The scenario where two or more threads read and write shared state without coordination, producing an incorrect or unpredictable result. Today's Producer-Consumer example reintroduces this exact scenario one level deeper, inside a shared `ArrayList`, even after a semaphore has already been introduced.

- **`synchronized` and its cost:** `synchronized` guarantees correctness by admitting exactly one thread at a time. Today's session opens by quantifying what that guarantee costs in terms of unused capacity.

- **`Lock` / `ReentrantLock` and the `try`/`finally` discipline:** Today's bounded buffer pattern reuses a `ReentrantLock` to protect the mutation of shared data, following the same `lock()`–`try`–`finally`–`unlock()` structure established last class.

This session also assumes comfort with `Runnable`, `Callable`, `Future`, and `ExecutorService` from Lecture 2, since the live demonstrations in this session are built on top of thread pools and `Callable` tasks introduced there.

## Connection to What Comes Next

This is the closing session of the concurrency module. The constructs introduced today — semaphores, bounded buffers, and the general discipline of reasoning about shared state — reappear directly inside backend low-level design: thread-safe singletons, connection pools, rate limiters, and in-memory caches are all built on exactly the primitives covered in this session and the three preceding it.

## Prerequisites

Confirm the following before the session:

- A working Java development environment (JDK and an IDE such as IntelliJ or VS Code).
- Familiarity with the Producer-Consumer `Store` class and the `synchronized (store)` fix from Lecture 3, since today's build directly extends that code.
- The homework submission from Lecture 2 (Multi-threaded Sum Calculation using `Callable` and `Future`), which is reviewed briefly at the start of this session.

## Reference Links

- Search "Java `java.util.concurrent.Semaphore` javadoc" for the official API reference on `acquire()`, `release()`, `acquire(int)`, and `release(int)`.
- Search "bounded buffer producer consumer pattern" for background on why capacity control and data-mutation control are treated as two separate concerns.
- Search "mutex vs semaphore" for a preview of the ownership distinction covered in this session — useful to read before class, since it is a frequently confused pair of concepts.

## What You Will Walk Away With

| Learning Outcome |
|-------------------|
| Define a semaphore formally, in terms of permits and the `acquire()` / `release()` operations. |
| Explain why `synchronized` limits a shared resource to a single concurrent user regardless of actual capacity, and how a semaphore removes that limitation. |
| Distinguish a binary semaphore from a counting semaphore, and explain why a semaphore with one permit behaves like a mutex. |
| Rebuild a Producer-Consumer system using two semaphores that signal each other, replacing a single coarse-grained lock. |
| Explain why a semaphore alone does not protect a shared data structure from concurrent mutation, and why a mutex is still required alongside it. |
| State the ownership distinction between a mutex and a semaphore, and explain why that distinction is both a strength and a risk. |
| Use `acquire(n)` and `release(n)` to enforce a fixed-size grouping of concurrent events. |
| Identify the standard semaphore failure modes — permit leaks, phantom permits, and multi-semaphore deadlock — and the habits that prevent each. |
