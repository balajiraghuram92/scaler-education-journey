Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/BkeBgqj7fg

# Post-Reads-Concurrency-4.md - HackMD

| POST-READ | Concurrency and Synchronization | Concurrency-4 — Synchronization with Semaphores |
|-----------|----------------------------------|--------------------------------------------------|

This document consolidates the material covered in the session. Each section states the relevant definition, walks through the Java code built live in class, and closes with the pitfalls most commonly associated with that concept. This is also the final session of the concurrency module; the closing sections summarize the module as a whole.

## Section 1: The Semaphore

### Definition

A **semaphore** is a synchronization construct that maintains an internal, non-negative count of available **permits**, and coordinates access to a shared resource across threads through two atomic operations:

- `acquire()` — decrements the permit count by one. If no permit is available, the calling thread blocks until one is released.
- `release()` — increments the permit count by one, and unblocks a waiting thread if one exists.

Conceptually, a semaphore performs the role of a coordinator managing a fixed number of available spots — comparable to a venue with a fixed seating capacity, where an arriving guest is admitted if a seat is free and made to wait otherwise, and a seat that is vacated is immediately offered to the next waiting guest.

### Mechanics

```java
Semaphore sem = new Semaphore(3); // 3 permits available
sem.acquire(); // take one permit -> 2 remain (blocks if 0 remain)
sem.release(); // return one permit -> 3 again
```

With three permits and five threads attempting to acquire concurrently, three threads proceed immediately and two block on `acquire()` until a permit is released. This is verifiable directly: running such a program produces a visible pause on the console after the first three threads begin work, followed immediately by the fourth thread proceeding the instant the first thread calls `release()`.

### Hidden Pitfalls

- **Assuming a semaphore tracks *which* thread holds a permit.** It does not. A semaphore only tracks a count. This is a deliberate design choice, revisited in Section 5.
- **Forgetting that `acquire()` blocks, not fails.** Unlike a method that might throw an exception or return a failure code when no permit is available, `acquire()` simply pauses the calling thread until a permit exists.

---

## Section 2: Binary vs. Counting Semaphores

### Definition

A **binary semaphore** is a semaphore initialized with exactly one permit. A **counting semaphore** is a semaphore initialized with more than one permit.

```text
Binary Semaphore = new Semaphore(1) -> one permit -> behaves like a mutex
Counting Semaphore = new Semaphore(N) -> N permits -> up to N threads admitted concurrently
```

A binary semaphore and a mutex are functionally equivalent in the simplest case: exactly one thread is admitted at a time, and all others wait. The mutex introduced in the previous lecture is, in effect, a semaphore that was never generalized beyond a single permit. A counting semaphore is the same construct with that restriction removed.

### Hidden Pitfalls

- **Treating a binary semaphore as identical to a mutex in every respect.** The two behave the same way for capacity, but differ in a property covered in Section 5 (ownership) that has no bearing on capacity at all.

---

## Section 3: Producer-Consumer, Rebuilt with Two Semaphores

### Deep-Dive Theory

The prior implementation used a single `synchronized (store)` block, which admitted exactly one thread into the store at a time, regardless of how many shelves were actually free. This session replaces that single lock with two independent counts:

- The number of **empty slots**, which determines how many producers may proceed.
- The number of **filled slots**, which determines how many consumers may proceed.

Two independent quantities require two independent semaphores.

```text
producerSemaphore = new Semaphore(5) -> 5 empty slots at start
consumerSemaphore = new Semaphore(0) -> 0 items available at start
```

The starting values describe the initial state of an empty store of capacity five: all five slots are free, and there is nothing yet to consume.

### Practical Mechanics

```java
public class Producer implements Runnable {
  private Store store;
  private Semaphore producerSemaphore;
  private Semaphore consumerSemaphore;

  Producer(Store store, Semaphore producerSemaphore, Semaphore consumerSemaphore) {
    this.store = store;
    this.producerSemaphore = producerSemaphore;
    this.consumerSemaphore = consumerSemaphore;
  }

  @Override
  public void run() {
    while (true) {
      try {
        producerSemaphore.acquire(); // wait for an empty slot
        store.addItem(new Object()); // occupy the slot
        consumerSemaphore.release(); // signal: an item is now available
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }
}
```

```java
public class Consumer implements Runnable {
  private Store store;
  private Semaphore producerSemaphore;
  private Semaphore consumerSemaphore;

  Consumer(Store store, Semaphore producerSemaphore, Semaphore consumerSemaphore) {
    this.store = store;
    this.producerSemaphore = producerSemaphore;
    this.consumerSemaphore = consumerSemaphore;
  }

  @Override
  public void run() {
    while (true) {
      try {
        consumerSemaphore.acquire(); // wait for an item
        store.removeItem(); // take the item
        producerSemaphore.release(); // signal: a slot is now free
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }
}
```

The mechanism worth internalizing here: a producer's `consumerSemaphore.release()` is not incrementing a counter for its own bookkeeping — it is a message to a different class of thread entirely, communicating that an item now exists. Symmetrically, a consumer's `producerSemaphore.release()` communicates that a slot has opened. Each side acquires its own semaphore and releases the other's:

```text
Producer: acquire(empty slot) -> add item -> release(item available)
Consumer: acquire(item) -> take it -> release(empty slot)
```

A semaphore, used this way, is not merely a counter — it functions as a signal passed between threads that never reference each other directly.

```java
public class Client {
  public static void main(String[] args) {
    Store store = new Store(5);
    Semaphore producerSemaphore = new Semaphore(5);
    Semaphore consumerSemaphore = new Semaphore(0);
    for (int i = 0; i < 8; i++) {
      new Thread(new Producer(store, producerSemaphore, consumerSemaphore)).start();
    }
    for (int i = 0; i < 20; i++) {
      new Thread(new Consumer(store, producerSemaphore, consumerSemaphore)).start();
    }
  }
}
```

With this structure, up to five producers may hold a producer permit simultaneously, meaning up to five producers can genuinely work in parallel — a direct improvement over the single-threaded-in-practice behaviour of the `synchronized` version.

### Hidden Pitfalls

- **Assuming more threads running concurrently automatically means correctness is preserved.** Increased concurrency increases, rather than decreases, the need to verify that shared state is still handled safely. Section 4 demonstrates exactly this gap.
- **Reversing which semaphore each role acquires versus releases.** A producer must acquire the producer semaphore and release the consumer semaphore, never the reverse; reversing the pattern breaks the signalling relationship entirely.

---

## Section 4: The Bounded Buffer Pattern — Semaphore for Capacity, Mutex for Mutation

### Deep-Dive Theory

The two-semaphore version above correctly limits *how many* producers may be active at once. It does not protect *what happens* once several producers are active simultaneously. If five producers are each permitted to call `store.addItem(...)` at the same moment, and that method performs `items.add(item)` on a plain, non-thread-safe `ArrayList`, the underlying list is still subject to a race condition — the same category of bug addressed in the previous lecture, occurring one level deeper. This distinguishes two separate concerns that a semaphore alone does not resolve:

```text
Capacity problem: how many threads may enter at once -> solved by the semaphore
Mutation problem: what happens when they touch shared data -> requires a separate lock
```

### Practical Mechanics

```java
public class Store {
  private int maxSize;
  private List<Object> items;
  private Lock lock = new ReentrantLock();

  public Store(int maxSize) {
    this.maxSize = maxSize;
    this.items = new ArrayList<>(maxSize);
  }

  public void addItem(Object item) {
    lock.lock();
    try {
      items.add(item);
    } finally {
      lock.unlock();
    }
  }

  public void removeItem() {
    lock.lock();
    try {
      items.remove(items.size() - 1);
    } finally {
      lock.unlock();
    }
  }
}
```

The `try`/`finally` structure ensures the lock is released even if an exception occurs during the mutation — the same discipline established in Lecture 3. The lock here protects only the brief moment of actually adding or removing an item from the list; any work a producer performs before calling `addItem` (reading a file, calling an external service, constructing the object) proceeds fully in parallel, unaffected by the lock. Parallelism is preserved everywhere except the single instant that genuinely requires exclusivity. This combination has a standard name:

> **Bounded buffer:** a shared, fixed-capacity data structure accessed by multiple producer and consumer threads, correctly synchronized using a pair of counting semaphores to track available capacity and available items, together with a mutex to protect the mutation of the underlying data structure itself.

```text
Counting semaphores -> HOW MANY may enter (capacity + availability)
Mutex / Lock -> protects the actual MUTATION of shared data
Both are required. They solve two different problems.
```

### Hidden Pitfalls

- **Assuming a semaphore makes a lock unnecessary, or vice versa.** They address different failure modes and are not substitutes for one another in this pattern.
- **Locking more than necessary.** Holding the lock for anything beyond the minimal mutation (for example, for the full body of work a producer performs) reintroduces the exact bottleneck the semaphore was meant to remove.

---

## Section 5: Semaphore vs. Mutex — The Ownership Difference

### Deep-Dive Theory

```text
Mutex: has an owner. Only the thread that acquired it may release it.
Semaphore: has no owner. Any thread may call release(), including a thread that never called acquire().
```

This is the defining structural difference between the two constructs, and it is directly visible in the Producer-Consumer implementation above: a consumer thread calls `producerSemaphore.release()` despite never having called `producerSemaphore.acquire()`. A strict mutex does not permit this — release is only valid for the thread holding the lock. A semaphore permits it by design, and that permission is precisely what makes cross-thread signalling possible: one thread acquiring and a different thread releasing is the entire mechanism by which producers and consumers coordinate without referencing each other. The same property is also the construct's principal risk. Because any thread may call `release()` at any time, an accidental or duplicate `release()` call silently inflates the permit count beyond the resource's actual capacity. A mutex cannot be over-released in this way, because only its owner may release it; a semaphore has no such check.

```text
No ownership is the strength: it enables cross-thread signalling.
No ownership is the danger: a stray release() inflates the count silently.
When to use which:
Only "one at a time" is required -> mutex / synchronized
"Up to N" or cross-thread signalling -> semaphore
```

### Hidden Pitfalls

- **Assuming a semaphore validates who is calling `release()`.** It does not, under any circumstance. This is not an oversight — it is the property that enables signalling.
- **Reaching for a semaphore when a mutex would be safer.** If a resource genuinely only ever needs "one thread at a time," a mutex's ownership check provides a safeguard a semaphore cannot offer.

---

## Section 6: Semaphore as a Baton — Enforcing Order (LeetCode 1116, Print Zero Even Odd)

### Deep-Dive Theory

Three threads — one printing `0`, one printing odd numbers, one printing even numbers — must together produce a strict interleaving such as `0102030405` for n = 5. This is not a capacity problem; it is an ordering problem. A semaphore can be used for this purpose as well, functioning here as a baton passed between threads rather than as a count of available capacity.

```text
zero semaphore -> starts at 1 (zero thread goes first)
odd semaphore -> starts at 0 (waits for zero's signal)
even semaphore -> starts at 0 (waits for zero's signal)
```

### Practical Mechanics

```java
class ZeroEvenOdd {
  private int n;
  private Semaphore zero = new Semaphore(1);
  private Semaphore odd = new Semaphore(0);
  private Semaphore even = new Semaphore(0);

  public ZeroEvenOdd(int n) {
    this.n = n;
  }

  public void zero(IntConsumer printNumber) throws InterruptedException {
    for (int i = 1; i <= n; i++) {
      zero.acquire();
      printNumber.accept(0);
      if (i % 2 == 0) even.release();
      else odd.release();
    }
  }

  public void odd(IntConsumer printNumber) throws InterruptedException {
    for (int i = 1; i <= n; i += 2) {
      odd.acquire();
      printNumber.accept(i);
      zero.release();
    }
  }

  public void even(IntConsumer printNumber) throws InterruptedException {
    for (int i = 2; i <= n; i += 2) {
      even.acquire();
      printNumber.accept(i);
      zero.release();
    }
  }
}
```

At program start, the odd and even threads immediately block on `acquire()`, since their semaphores are initialized to zero. Only the zero thread can proceed. After printing `0`, it releases either the odd or the even semaphore depending on which number is due next; the released thread prints its number and immediately hands control back to the zero thread by calling `zero.release()`. The result is a strict, repeatable relay: zero, number, zero, number, with no possibility of interleaving out of order.

```text
Semaphore, two uses so far:
as a COUNTER -> "how many may act" (the bounded buffer)
as a BATON -> "whose turn is it" (Print Zero Even Odd)
```

### Hidden Pitfalls

- **Confusing "starts at 0" with "broken."** A semaphore initialized to zero is a deliberate and common pattern — it guarantees the corresponding thread cannot proceed until explicitly signalled by another thread.
- **Forgetting to hand control back.** Each number-printing thread must release the zero semaphore before its next iteration; omitting this call halts the relay permanently.

---

## Section 7: Semaphore for Grouping — `acquire(n)` and `release(n)` (LeetCode 1117, Building H2O)

### Deep-Dive Theory

Hydrogen and oxygen threads arrive independently and must only print in valid groups of two hydrogen atoms and one oxygen atom (`HHO`, `HOH`, or `OHH`), never in any other grouping such as three hydrogens with no oxygen. This requires a thread to wait until a specific number of other events have occurred before proceeding — a requirement that the single-permit `acquire()` used so far cannot express directly. `Semaphore` supports acquiring and releasing more than one permit at a time:

```text
acquire(n) -> block until n permits are available, then take all n at once
release(n) -> return n permits at once
```

```text
h semaphore -> starts at 2 (allow two hydrogens through per molecule)
o semaphore -> starts at 0 (oxygen blocked until both hydrogens signal)
```

### Practical Mechanics

```java
class H2O {
  Semaphore h = new Semaphore(2);
  Semaphore o = new Semaphore(0);

  public void hydrogen(Runnable releaseHydrogen) throws InterruptedException {
    h.acquire();
    releaseHydrogen.run();
    o.release();
  }

  public void oxygen(Runnable releaseOxygen) throws InterruptedException {
    o.acquire(2);
    releaseOxygen.run();
    h.release(2);
  }
}
```

Two hydrogen threads may pass `h.acquire()` before a third is blocked, since `h` starts at two permits; a third hydrogen thread arriving before the next molecule begins is forced to wait, which is exactly what prevents an invalid `HHH` grouping. Each hydrogen thread that proceeds calls `o.release()`, raising the oxygen semaphore's count by one per hydrogen. The oxygen thread is blocked at `o.acquire(2)` until both hydrogens have signalled; only then does it proceed, after which it calls `h.release(2)` to reopen both hydrogen slots for the next molecule.

```text
Semaphore, three uses in total:
COUNTER -> "how many may act" (the bounded buffer)
BATON -> "whose turn is it" (Print Zero Even Odd)
GROUPING -> "assemble n, then proceed" (Building H2O)
```

This grouping pattern generalizes to batch processing, request aggregation, and barrier-style synchronization in production systems, wherever a fixed number of independent events must complete before a dependent action can proceed.

### Hidden Pitfalls

- **Assuming `acquire(n)` takes permits one at a time as they arrive.** It blocks until all n permits are simultaneously available, then takes them atomically as a single operation.
- **Mismatching the acquire and release counts.** `release(2)` must correspond to a semaphore intended to be acquired with `acquire(2)`; an inconsistent count silently corrupts the intended grouping size.

---

## Section 8: Common Semaphore Pitfalls

### Deep-Dive Theory

Because a semaphore has no ownership (Section 5), it is subject to a distinct set of failure modes that a mutex, by virtue of its ownership check, largely prevents.

```text
1. Forgot to release() -> permits leak. Eventually all permits are exhausted, every waiting thread blocks indefinitely, the program freezes.
2. release() without a matching acquire() -> a phantom permit is created. The permit count exceeds the resource's real capacity, and no error is raised.
3. Wrong initial count -> Semaphore(0) when Semaphore(1) was intended: no thread ever proceeds. Semaphore(5) when 1 was intended: no real protection is enforced.
4. Multi-semaphore deadlock -> Thread A holds semaphore 1 and waits on semaphore 2. Thread B holds semaphore 2 and waits on semaphore 1. Neither can proceed. Prevention: every thread must acquire multiple semaphores in the same fixed order.
5. Missing try/finally -> an exception raised between acquire() and release() causes the permit to never be returned, producing the same effect as (1).
```

Of these, a forgotten `release()` (case 1) fails loudly — the program eventually freezes entirely, which is difficult to miss. An extra `release()` (case 2) fails silently — the declared capacity limit is quietly violated, and the resulting corruption may only surface intermittently. The absence of ownership is precisely what makes case 2 possible; a mutex would reject an unmatched unlock outright.

### Practices That Prevent Most of These

```text
- Always call release() inside a finally block.
- When multiple semaphores must be acquired by the same thread, acquire them in a single, consistent order across the entire codebase.
```

### Hidden Pitfalls

- **Treating a silent capacity violation as a rare edge case.** Because it produces no exception, it is often mistaken for a low-priority or intermittent bug rather than a structural defect in how permits are being released.
- **Applying the same-order rule inconsistently.** The deadlock prevention rule only holds if every code path that acquires multiple semaphores follows the identical order; a single exception anywhere in the codebase reintroduces the risk.

---

## Section 9: Module Summary

This session closes a four-lecture sequence on concurrency. Consolidated across all four:

```text
Lecture 1: Process vs. thread. A single core executes one thread at a time. Concurrency (an illusion of simultaneity) vs. parallelism (genuine simultaneity). The Runnable interface. Thread execution order is not guaranteed.

Lecture 2: Excess threads relative to available cores reduce, not improve, throughput -> thread pools (fixed vs. cached), ExecutorService. Callable and Future, for tasks that return a result. Multithreaded merge sort as an example where separate memory per thread requires no synchronization at all.

Lecture 3: Shared, mutable memory accessed by multiple threads is where correctness risk originates: race condition, critical section, pre-emption. Fixed using a mutex, expressed in Java as a synchronized block or method. synchronized is correct, but restricted to exactly one thread at a time regardless of actual capacity.

Lecture 4: A semaphore generalizes "one at a time" to "up to N at a time," and additionally functions as a cross-thread signal. A bounded buffer combines a semaphore (for capacity) with a mutex (for mutation). A semaphore has no ownership, which is both its defining strength and its principal risk. The same construct also enforces strict ordering (Print Zero Even Odd) and grouping (Building H2O).
```

The module reduces to two statements:

```text
Separate memory between threads is inherently safe.
Shared, mutable memory is not, and requires explicit protection — either a single lock restricting access to one thread at a time, or a semaphore permitting up to N threads with explicit signalling between them.
```

These constructs recur directly in backend low-level design: thread-safe singletons, connection pools, rate limiters, and in-memory caches are each built from the primitives covered across this module.

---

## Section 10: Key Terminology

| Term | Definition |
|------|------------|
| **Semaphore** | A synchronization construct maintaining a count of available permits, with `acquire()` and `release()` as its atomic operations |
| **Permit** | The unit of availability tracked by a semaphore; `acquire()` consumes one, `release()` returns one |
| **Binary semaphore** | A semaphore initialized with exactly one permit; functionally equivalent to a mutex for capacity control |
| **Counting semaphore** | A semaphore initialized with more than one permit, admitting up to that many threads concurrently |
| **Bounded buffer** | A fixed-capacity shared structure synchronized using counting semaphores for capacity and a mutex for mutation |
| **Ownership (mutex)** | The property whereby only the thread that acquired a mutex may release it |
| **No ownership (semaphore)** | The property whereby any thread may call `release()`, independent of whether it ever called `acquire()` |
| **`acquire(n)` / `release(n)`** | Variants that take or return n permits atomically as a single operation, used to enforce grouping |
| **Permit leak** | A bug in which permits are acquired but never released, eventually exhausting the semaphore and blocking all threads |
| **Phantom permit** | A bug in which `release()` is called without a matching `acquire()`, inflating the permit count above true capacity |

---

## Section 11: Self-Check Questions

1. Explain, in one or two sentences, why `synchronized` correctly prevents the crash from Lecture 3 but still leaves a real inefficiency unresolved.
2. Predict the console behaviour: a `Semaphore` is created with 3 permits, and 5 threads attempt to `acquire()` it simultaneously, each holding the permit for one second before releasing.
3. In the two-semaphore Producer-Consumer implementation, why does the producer thread call `consumerSemaphore.release()` rather than `producerSemaphore.release()`?
4. A `Store.addItem()` method is protected only by a `producerSemaphore.acquire()` call and no lock. Explain precisely what can still go wrong, even though the semaphore is functioning correctly.
5. State the one structural difference between a mutex and a semaphore that makes cross-thread signalling possible with a semaphore but not with a strict mutex.
6. In the Print Zero Even Odd implementation, why are the `odd` and `even` semaphores initialized to 0 rather than 1?
7. In the Building H2O implementation, what specifically prevents a third hydrogen thread from printing before the current molecule's oxygen thread has proceeded?
8. Explain the difference in failure symptoms between a forgotten `release()` and an extra, unmatched `release()`. Which is typically harder to detect, and why?
9. Two threads must each acquire two different semaphores, `sem1` and `sem2`, to complete their work. What specific rule prevents these two threads from deadlocking against each other?
10. Why is `try`/`finally` used around `acquire()`/`release()` pairs in every example in this document?

---

## Section 12: Further Reading

- **Official Java documentation — `java.util.concurrent.Semaphore`:** the canonical reference for `acquire()`, `release()`, and their multi-permit variants.
- **Official Java documentation — `java.util.concurrent.locks.ReentrantLock`:** the reference for the mutex construct used alongside the semaphore in the bounded buffer pattern.
- **LeetCode 1115 — Print FooBar Alternately, LeetCode 1116 — Print Zero Even Odd, LeetCode 1117 — Building H2O:** the problem set this session's baton and grouping patterns were drawn from.
- General reading on the **bounded buffer** and **producer-consumer** patterns, and on **deadlock prevention through consistent lock ordering**.

---

## Section 13: Homework

```text
1. Build the two-semaphore bounded buffer Producer-Consumer from this session independently, with capacity 3 and a Lock protecting the Store. Add output showing how many producers/consumers are active at once, and confirm more than one is active simultaneously.
2. Solve LeetCode 1115, "Print FooBar Alternately," using two semaphores.
3. Re-solve LeetCode 1116 and 1117 without referring to this document. For each, write one line identifying whether the semaphore is being used as a counter, a baton, or a grouping mechanism.
4. Deliberately introduce one extra producerSemaphore.release() call at an incorrect point in the bounded buffer implementation. Run it, observe the capacity limit being violated, and record one line explaining why, referencing the ownership discussion in Section 5.
5. Implement the BankAccount class below with synchronized methods, create 5 depositing and 5 withdrawing threads running concurrently, and verify the final balance is correct. public class BankAccount { private Long balance = 0L; public void deposit(Long amount) { if (amount > 0) { balance += amount; } } public void withdraw(Long amount) { if (balance >= amount && amount > 0) { balance -= amount; } } }
6. Create a list of 100 dummy URLs and simulate scraping each with a 200ms delay. Run the simulation once using a FixedThreadPool(10) and once using a CachedThreadPool. Record and compare total execution time.
7. Push all code to GitHub.
```
