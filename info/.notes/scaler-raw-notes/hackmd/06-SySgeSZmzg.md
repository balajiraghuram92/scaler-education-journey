Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/SySgeSZmzg

# Concurrency-2: Executors, Callable & Parallel Decomposition

## Overview

This session builds on Concurrency-1 by addressing scalability challenges when creating individual threads becomes wasteful. The course introduces thread pools, which maintain a roster of reusable workers rather than creating new threads for each task.

## Core Learning Objectives

The session covers four main blocks:

1. **Thread Pool Motivation** - Why one-thread-per-task doesn't scale, exploring thread creation overhead and idle thread waste
2. **Executor Framework** - Factory methods, ExecutorService handles, and execute() versus submit()
3. **Result Retrieval** - Using Callable and Future to get computed values back from threads
4. **Practical Application** - Building a multithreaded Merge Sort using parallel decomposition

## Key Principles

Two fundamental concepts guide the material:

**Reuse Over Recreation**: "Creating a new thread for every task...does not scale. Creating a thread costs time and memory" (paraphrased from content). Thread pools maintain a small, fixed set of reusable threads.

**Submit-First/Collect-Last Pattern**: "Calling `get()` immediately after submitting one task...silently turns parallel work back into serial work" (condensed from source). Submit all tasks before retrieving results to maintain genuine parallelism.

## Real-World Analogies

- Thread pools mirror restaurant kitchens: fixed staff handles variable order volume
- FixedThreadPool vs CachedThreadPool parallel hospital staffing strategies
- Callable and Future function like dry-cleaning claim tickets

## Prerequisites

Students should review Concurrency-1 concepts including Runnable, thread creation, and non-deterministic execution order before attending.