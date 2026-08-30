Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/rJeBxlS-7zl

# Lecture 6: Pre-Read Summary – Concurrency, Processes, and Threads

## Overview

This lecture introduces how programs execute at the system level, moving from object-oriented design theory to the runtime reality of concurrent execution. The session uses an office metaphor throughout: a company as a running application, employees as execution units, managers as CPU schedulers, and desks as physical processing resources.

The content is structured into four progressive blocks:

1. **From Code to Process**: Covers compilation, executables, the distinction between programs and processes, RAM usage, and the Process Control Block (PCB)
2. **Workers Inside a Process**: Explores threads, program counters, call stacks, shared memory, and the CPU scheduler
3. **Concurrent Execution**: Addresses concurrency versus parallelism, single-core versus multi-core systems, and context switching
4. **Java Implementation**: Introduces the Runnable interface, thread creation with `start()` versus `run()`, and non-deterministic execution order

## Why This Matters

Real backend systems handle multiple simultaneous operations. A web server doesn't process one user completely, then move to the next—it serves thousands concurrently. Understanding these concepts distinguishes production-ready code from single-user scripts. The session emphasizes a critical vocabulary distinction and a common point of confusion among engineers: the difference between concurrency and parallelism.

## Real-World Use Cases

**Process**: Modern browser tabs often run in separate processes; one tab's crash won't affect others due to isolated memory spaces.

**Thread**: A video game runs multiple threads within one process—one handles graphics rendering, another manages audio, a third processes controller input, and a fourth autosaves progress. All share the game's memory.

**CPU Scheduler**: Web servers with more incoming requests than processing capacity use schedulers to determine execution order, ensuring no request starves while preventing excessive switching.

**Concurrency**: A single-core server handling 1,000 simultaneous users achieves this through rapid context switching, giving each user the illusion of constant attention despite only one request actively advancing at any moment.

**Parallelism**: The same server on multi-core hardware processes multiple requests literally simultaneously, with one request per core advancing in true parallel.

**Context Switching**: When a CPU pauses one thread to resume another, it incurs overhead similar to a human losing their place while context-switching during studying—real time spent on logistics rather than work.

**Runnable**: A scheduled report defines *what* needs doing without specifying *which* worker performs it, exactly like handing a written task to whichever employee is available.

## Core Conceptual Framework

Two foundational ideas shape the entire session:

**Concurrency vs. Parallelism**: "Concurrency is dealing with many things at once. Parallelism is doing many things at once." The distinction emerges from two diagnostic questions:
- How many tasks are partially done simultaneously?
- How many tasks actively advance right now?

One employee switching between multiple reports shows many partial tasks but only one advancing—that's concurrency. Five employees at five desks, each working independently, show many partial tasks *and* many advancing simultaneously—that's parallelism.

**Task-Centric Thinking**: Rather than thinking in terms of threads, developers should think in terms of tasks, not threads — a thread is just the medium that carries out a task. This mindset—defining what needs doing, then assigning it to an available worker—mirrors real-world task delegation.

## Prerequisites from Prior Learning

The course assumes familiarity with OOP concepts:

- **Interfaces and Contracts**: Similar to how `Book` implements `Lendable`, student code will implement `Runnable`
- **Method Overriding**: Implementing `Runnable`'s single method parallels previous `displayDashboard()` overrides
- **Object State**: Task objects carry their own data via constructors, as `Member` objects carried `borrowedBooksCount`
- **Collections and Iteration**: Creating and distributing multiple task objects mirrors iterating through `List<User>`

## Learning Outcomes

By session's end, students will:

1. Explain the journey from source code to executing process and RAM's role
2. Distinguish processes from threads, identifying what each owns versus shares
3. Define the Process Control Block and the CPU Scheduler's role
4. Differentiate concurrency from parallelism using diagnostic questions
5. Explain context switching overhead and performance implications
6. Implement `Runnable`, create threads, and use `start()` correctly
7. Articulate why thread output order is non-deterministic and why it matters

## Environment Setup Requirements

- Recent JDK (Java 17+) with verified compilation capability
- IDE (IntelliJ IDEA Community or VS Code with Java Extension Pack)
- Empty project for live coding
- Process monitor (Activity Monitor, Task Manager, or `top`/`htop`) for observing live thread counts

No external libraries are required; all materials use standard Java.

## Transition to Next Topic

The session ends with an intentional open question: what happens when two threads edit the same shared file simultaneously? This BookMyShow seat-booking scenario bridges to the next session covering Thread Pools, Executors, Callable, and Future—all building directly on today's `Runnable` foundation.

Note: This is a detailed structured summary (not verbatim) — the initial verbatim-extraction attempt was refused by the fetch tool on copyright grounds; this summary-style retry succeeded instead.
