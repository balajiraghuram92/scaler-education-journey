Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/r1WMg1SXGe

# Lecture 6: Pre-Read - Concurrency-1

## Overview

This lecture introduces concurrent programming fundamentals. The instruction moves through four blocks:

1. **Program to Process**: Covers compilation, executables, RAM, and Process Control Blocks
2. **Threads Within**: Explores Program Counters, Call Stacks, and shared memory
3. **Concurrent Execution**: Distinguishes concurrency from parallelism and context switching
4. **Java Implementation**: Introduces `Runnable` interface and thread creation

## Core Distinction

The material emphasizes a foundational contrast: "Concurrency involves managing multiple simultaneous undertakings, while parallelism means executing them genuinely at the same moment."

To differentiate, ask:
- How many tasks show partial completion now?
- How many tasks currently advance?

Single-core systems with rapid switching enable concurrency; multi-core systems enable true parallelism.

## Key Vocabulary

- **Process**: Independent program execution with isolated memory
- **Thread**: Worker unit within a process sharing memory
- **CPU Scheduler**: Decision-maker for execution order
- **Context Switching**: State preservation when pausing one worker for another
- **Runnable**: Interface defining task behavior separate from execution

## Prerequisites from Prior Study

Knowledge of interfaces, method overriding, object state management, and collection iteration carry forward from previous OOP coursework.

## Learning Outcomes

Students will explain process-to-execution journeys, distinguish processes from threads, describe the Process Control Block, differentiate concurrency from parallelism, understand context switching overhead, implement `Runnable` correctly, and recognize non-deterministic output ordering in concurrent code.

## Setup Requirements

- JDK 17 or later
- IDE (IntelliJ or VS Code)
- Empty project ready for live coding
- System process monitor available