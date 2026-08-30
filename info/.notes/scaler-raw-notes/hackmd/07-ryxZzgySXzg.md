Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/ryxZzgySXzg

# Post-Reads_Concurrency2.md - HackMD

## Overview

This document consolidates a Concurrency-2 session on executors and callables, using an office analogy where "company = process pool, employee = thread, task = unit of work (Callable/Runnable), manager = scheduler, claim slip = Future, desk = core."

## Section 1: The Too-Many-Threads Problem, and Thread Pools

**Core Issue**: Creating one thread per task doesn't scale. A single-core machine runs one thread at a time; an eight-core machine runs eight threads simultaneously. Creating 100 threads means most remain idle.

**Two Costs**:
- Creation cost: thread creation requires real time and memory
- Idle waste: threads finish tasks quickly then remain idle

**Solution**: Maintain a smaller, fixed set of reusable workers. Tasks queue while workers pick up next items when free.

**Thread Pool Creation**:
```java
ExecutorService fixed = Executors.newFixedThreadPool(5);
ExecutorService cached = Executors.newCachedThreadPool();
```

**FixedThreadPool**: Exact, unchanging thread count. With 100 tasks and 5 threads, only 5 execute simultaneously; 95 wait in queue.

**CachedThreadPool**: No fixed size. Creates temporary threads when needed; terminates idle threads.

**Example with NumberPrinter**:
```java
ExecutorService pool = Executors.newFixedThreadPool(5);
for (int i = 1; i <= 20; i++) {
    pool.execute(new NumberPrinter(i));
}
pool.shutdown();
```

With FixedThreadPool(5), exactly 5 thread names appear across 20 tasks, with internal queue holding waiting tasks.

**Hidden Pitfalls**:
- Assuming more threads always means more speed
- Choosing CachedThreadPool by default (unbounded pool risks unexpectedly large thread counts)
- Forgetting queued tasks aren't yet running

## Section 2: The Executor Framework

**Terminology**:
- Executors = factory that builds thread pools
- ExecutorService = handle for handing tasks to pools

**Executor Interface**:
```java
public interface Executor {
    void execute(Runnable command);
}
```

Purpose: Decouple task submission from execution mechanics (threading, scheduling, thread reuse).

**ExecutorService**: Sub-interface adding lifecycle management and submit() method, which accepts Callable/Runnable and returns Future.

**Executors**: Utility class with static factory methods like newFixedThreadPool(int) and newCachedThreadPool().

**Practical Usage**:
```java
ExecutorService pool = Executors.newFixedThreadPool(5);
pool.execute(someRunnable);           // fire and forget
pool.submit(someCallable);            // returns Future
```

execute() accepts Runnable, returns nothing. submit() accepts Callable or Runnable, immediately returns Future.

**Hidden Pitfalls**:
- Confusing Executors (factory only) with ExecutorService (actual pool handle)
- Using execute() when result is needed (only works with submit() and Callable)

## Section 3: Executor Lifecycle

Pool threads don't stop after work completes; they remain alive waiting for next tasks, like employees staying on clock until office closes.

**shutdown() Method**:
```java
pool.shutdown();
```

Initiates orderly shutdown: stops accepting new work, finishes queued tasks, then closes. Does not block; caller continues while pool finishes in background.

**Related Methods**:
- shutdownNow(): drops queued tasks, attempts immediate stop
- awaitTermination(t, unit): blocks caller until tasks finish or timeout elapses

**Critical Point**: Without shutdown(), program prints correct output but JVM never exits—pool threads remain alive and waiting.

**Hidden Pitfalls**:
- Forgetting shutdown() (most common real-world Executor bug)
- Expecting shutdown() to immediately stop in-progress work (it doesn't)

## Section 4: Callable and Future

**Problem**: Runnable's run() returns void, structurally preventing result return to caller. Sorting half a list needs to return that half for merging.

**Callable Interface**:
```java
public interface Callable<V> {
    V call() throws Exception;
}
```

Similar to Runnable but task can return result and throw checked exception.

**Future Interface**: Represents eventual result of asynchronous computation. Provides get() to retrieve result (blocks until ready).

**Implementation Example**:
```java
class NumberGenerator implements Callable<Integer> {
    private int n;
    public NumberGenerator(int n) { this.n = n; }
    @Override
    public Integer call() throws Exception {
        int sum = 0;
        for (int i = 1; i <= n; i++) sum += i;
        return sum;
    }
}
```

**Usage Pattern**:
```java
Future<Integer> f = pool.submit(new NumberGenerator(9));
System.out.println("main keeps going...");
int result = f.get();  // BLOCKS until ready
System.out.println(result);  // 45
```

submit() doesn't block; execution continues immediately. Only get() pauses caller until task finishes.

**Critical Pattern—Submit-First/Collect-Last**:
```java
// WRONG—becomes serial
int a = pool.submit(taskA).get();
int b = pool.submit(taskB).get();

// RIGHT—parallel
Future<Integer> fa = pool.submit(taskA);
Future<Integer> fb = pool.submit(taskB);
int total = fa.get() + fb.get();
```

First version blocks after submitting A, so B only starts after A finishes—serial execution. Second version submits both first, collecting results afterward—genuinely parallel.

**Key Rule**: "get() waits. Submit everything FIRST, collect at the END."

**Hidden Pitfalls**:
- Calling get() right after submit() in task loops (most common parallelism bug)
- Assuming submit() blocks (only get() blocks)
- Forgetting Callable.call() can throw checked exception

## Section 5: Multithreaded Merge Sort (Parallel Decomposition)

Merge Sort naturally fits parallel execution since recursive halves never touch each other's data:

```text
Merge Sort:
1. SPLIT list into two halves
2. SORT each half (recursively)
3. MERGE sorted halves back together
```

Left and right halves are completely independent throughout sort—opportunity for different threads. Must use Callable since Runnable's void run() cannot return sorted sub-list.

**Implementation**:
```java
public class MergeSortTask implements Callable<List<Integer>> {
    private final List<Integer> list;
    private final ExecutorService pool;
    
    public MergeSortTask(List<Integer> list, ExecutorService pool) {
        this.list = list;
        this.pool = pool;
    }
    
    @Override
    public List<Integer> call() throws Exception {
        if (list.size() <= 1) return list;
        
        int mid = list.size() / 2;
        List<Integer> left = new ArrayList<>(list.subList(0, mid));
        List<Integer> right = new ArrayList<>(list.subList(mid, list.size()));
        
        // Submit BOTH first
        Future<List<Integer>> leftFuture = pool.submit(new MergeSortTask(left, pool));
        Future<List<Integer>> rightFuture = pool.submit(new MergeSortTask(right, pool));
        
        // Collect AFTER
        List<Integer> sortedLeft = leftFuture.get();
        List<Integer> sortedRight = rightFuture.get();
        
        return merge(sortedLeft, sortedRight);
    }
    
    private List<Integer> merge(List<Integer> a, List<Integer> b) {
        List<Integer> result = new ArrayList<>();
        int i = 0, j = 0;
        while (i < a.size() && j < b.size()) {
            if (a.get(i) <= b.get(j)) result.add(a.get(i++));
            else result.add(b.get(j++));
        }
        while (i < a.size()) result.add(a.get(i++));
        while (j < b.size()) result.add(b.get(j++));
        return result;
    }
}
```

**Client Code**:
```java
ExecutorService pool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors());
List<Integer> data = /* big list of random numbers */;
Future<List<Integer>> result = pool.submit(new MergeSortTask(data, pool));
System.out.println(result.get());
pool.shutdown();
```

**The Shared-Executor Pitfall**: Creating new pool inside call() for every recursive task is incorrect:
```java
// DON'T DO THIS
public List<Integer> call() {
    ExecutorService myOwnPool = Executors.newFixedThreadPool(4);
    // disaster...
}
```

Every recursive call would spin up its own pool, creating thousands of pools reproducing too-many-threads problem multiplied across recursion tree. Correct approach: pass single shared ExecutorService through constructor, reusing it at every recursion level.

**Rule**: "One shared executor for the whole job. NEVER a pool per task."

**Production Notes**:
- Pool starvation: task blocked on get() still occupies thread slot even though CPU core sits idle. Deep recursion with small fixed pool can stall entire job.
- ForkJoinPool with work-stealing exists specifically to avoid this failure mode
- Cutoff: splitting to single elements creates ~2n tasks for n elements. Production would stop splitting below threshold (e.g., 1000 elements) and sort directly.

**Hidden Pitfalls**:
- Creating new ExecutorService inside recursive task (explosion of pools/threads)
- Calling get() on left half's Future before submitting right half (silently serializes)
- Ignoring pool starvation on small, fixed pool

## Section 6: Putting It All Together — Today's Full Picture

```text
Thread creation overhead (Concurrency-1)
  -> motivates reusable Thread Pool
Executors (factory)
  -> builds FixedThreadPool / CachedThreadPool
ExecutorService (handle)
  -> execute() for Runnable, submit() for Callable/Runnable
Callable<V>
  -> call() returns V, unlike Runnable's void run()
Future<V>
  -> claim slip; get() blocks until result ready
shutdown()
  -> stops accepting new work, finishes queue, closes
Merge Sort
  -> split -> sort halves PARALLEL via submit-first/collect-last -> merge
```

**Concept Reference Table**:

| Concept | Where it appears | What it does |
|---------|------------------|--------------|
| Thread pool | Executors.newFixedThreadPool(5) | Reusable, bounded (or elastic) thread set draining task queue |
| Executors | Factory calls throughout | Builds different ExecutorService kinds |
| ExecutorService | pool in every demo | Handle tasks submitted to |
| execute() | pool.execute(new NumberPrinter(i)) | Runs Runnable, fire and forget, no return value |
| submit() | pool.submit(new NumberGenerator(9)) | Runs Callable (or Runnable), returns Future |
| shutdown() | End of every executor demo | Stops accepting new tasks, finishes queue, closes |
| Callable<V> | NumberGenerator, MergeSortTask | Task with call() returning value, throwing Exception |
| Future<V> | leftFuture, rightFuture, result | Pending async task result; get() blocks until ready |
| Submit-first/collect-last | MergeSortTask.call() | Keeps independent tasks genuinely running parallel |
| Shared executor | pool passed through MergeSortTask constructor | Prevents uncontrolled pool explosion across recursion |

These ideas build directly on each other. Thread pool exists because creating threads one at a time doesn't scale. ExecutorService is interface exposing pool. Callable and Future exist because Runnable cannot report result. Merge Sort applies all four pieces—thread pool, ExecutorService, Callable, Future—to real divide-and-conquer problem.

**Preview of Next Class**: Merge Sort stayed safe because left/right halves never shared memory. What happens when two threads write to same shared memory simultaneously? Today's answer: avoid by design. Next class: multiple threads write to same shared data purposely, showing resulting corruption—same problem as two people booking last seat on BookMyShow simultaneously.

```text
Separate memory = safe.
Shared memory = danger.
  -> Concurrency-3
```

## Section 7: Key Terminology

| Term | Definition |
|------|------------|
| **Thread pool** | Managed, reusable thread set executing submitted tasks from work queue, avoiding cost of creating new thread per task |
| **Executor** | Interface (java.util.concurrent) representing object executing submitted Runnable tasks, decoupling task submission from execution mechanics |
| **Executors** | Utility class providing static factory methods (newFixedThreadPool, newCachedThreadPool) constructing configured ExecutorService instances |
| **ExecutorService** | Sub-interface of Executor adding lifecycle management and submit(), returning Future representing task's pending result |
| **FixedThreadPool** | Thread pool with exact, unchanging thread count; excess tasks wait in queue |
| **CachedThreadPool** | Thread pool with no fixed size; creates new threads for task burst, terminates idle threads |
| **execute()** | Executor/ExecutorService method running Runnable with no return value |
| **submit()** | ExecutorService method running Callable (or Runnable), immediately returning Future |
| **shutdown()** | Initiates orderly executor shutdown: no new tasks accepted, queued and running tasks completed first |
| **shutdownNow()** | Attempts immediate shutdown: drops queued tasks, tries stopping all running tasks right away |
| **awaitTermination(timeout, unit)** | Blocks calling thread until all tasks finish or timeout elapses, whichever comes first |
| **Callable<V>** | Functional interface (java.util.concurrent) with task defined by V call() throws Exception, allowing result return and checked exception throwing |
| **Future<V>** | Interface representing eventual asynchronous computation result; provides get() to retrieve result, blocking if not yet ready |
| **get()** | Future method blocking calling thread until associated task's result available, then returning it |
| **Submit-first/collect-last** | Pattern of submitting every independent task before calling get() on any Futures, so all tasks run concurrently |
| **Parallel decomposition** | Splitting problem into independent sub-problems solvable on separate threads, combining results |
| **Pool starvation** | Situation where every fixed pool thread blocks waiting on get() for task with no free thread left to run it, stalling job while CPU appears idle |
| **ForkJoinPool** | Specialised executor with work-stealing, designed for divide-and-conquer workloads reducing pool starvation risk |

## Section 8: Self-Check Questions

1. A classmate says "we should always use CachedThreadPool, since it never makes a task wait." Identify the flaw in this reasoning, and describe a workload where FixedThreadPool is clearly better.

2. Explain, precisely, why Runnable cannot be used for MergeSortTask in today's class. Which single detail about run()'s signature makes this impossible?

3. Future<Integer> f = pool.submit(task); is followed by int x = f.get();. Is this code correct? If two independent tasks are submitted this way back-to-back, what happens to their parallelism, and why?

4. A program prints all expected output then never terminates. Name single most likely missing line, explain in terms of pool thread behavior why program hangs.

5. Trace through MergeSortTask.call() for 8-element list. At what point are leftFuture and rightFuture both "in flight" simultaneously, and what changes if leftFuture.get() called immediately after creation?

6. Why is ExecutorService passed into MergeSortTask's constructor rather than created inside call()? Describe concretely what happens to large sort if each recursive call creates own pool.

7. Define pool starvation in own words, connect it to why program shows near-zero CPU usage in monitoring tool while completely stalled.

8. Callable<V>'s call() declared as V call() throws Exception. What does this allow that Runnable's void run() does not, in two distinct ways?

## Section 9: Further Reading

- **The Java Tutorials (Oracle) — "Executors" and "Concurrent Collections" lessons**: official walkthrough of Executor framework, thread pools, and Executors factory methods.

- **Oracle Java API docs — Executor, ExecutorService, Executors, Callable, Future**: precise interface contracts for everything used in today's class, including exact shutdown(), shutdownNow(), and get() behavior.

- **Oracle Java API docs — ForkJoinPool**: referenced today as production-grade alternative for divide-and-conquer workloads like Merge Sort; worth first read despite out-of-scope implementation today.

## Section 10: Homework

```
1. Write multithreaded sum of 1,000,000 numbers across N cores using Callable and Future. Extend today's NumberGenerator pattern and last class's availableProcessors() homework into real parallel computation, combining individual results yourself.

2. In Merge Sort, add print inside call() showing which thread sorted which sub-list.

3. Deliberately break it: create NEW pool inside call(), run on large array, observe meltdown, write one line explaining why it happens.

4. Push code to GitHub.
```

## Looking Ahead: Synchronization

This previewed in class but **not** taught today; treat only as heads-up, not revision material yet:

- Today's Merge Sort stayed safe because threads never shared memory; left/right halves were entirely separate lists. Safety disappears moment multiple threads read/write **same** shared data simultaneously; one thread's update silently overwrites another's, no error thrown.

- Concurrency-3 introduces **synchronization**, mechanisms Java provides (starting with synchronized keyword) to make shared data safe when several threads access concurrently, using same booking-collision scenario—two requests, one seat, same instant—Concurrency-1 first raised.

Next session builds directly on today's Executor and Callable work to demonstrate failure live before introducing tools fixing it.