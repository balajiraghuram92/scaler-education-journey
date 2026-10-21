# Bytecode, the Evaluation Loop and the GIL

When a hot path is slow, when a thread-safety claim is wrong, or when someone asks whether the new free-threaded build lets them drop `multiprocessing`, the answer lives in how CPython executes your code. Senior interviews probe this layer: "what does `dis` show for this line?", "why doesn't a thread pool speed up this loop?", "what actually changes in 3.13t?". This lesson gives you the execution model well enough to reason from first principles instead of memorizing rules of thumb.

## Concepts Covered

### From source to bytecode to the evaluation loop

CPython compiles source to an AST, then to **bytecode** stored in a **code object**, then interprets that bytecode in a C evaluation loop (`_PyEval_EvalFrameDefault`). Imported modules are cached as `.pyc` files in `__pycache__`, keyed by interpreter magic number and either the source mtime or a hash, so compilation cost is paid once per change. Bytecode is an implementation detail: opcode names, numbering and cache layout change between minor versions, so never write code that depends on them. Use `dis` to understand, not to parse.

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

```text
  2           RESUME                   0

  3           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

That output is from 3.13. Read it as a stack machine: the left column is the source line, then the opcode, its argument and a human-readable annotation. `LOAD_FAST_LOAD_FAST` is a 3.13 superinstruction that loads two locals at once; older versions show two `LOAD_FAST` lines. `BINARY_OP` pops two values and pushes the result. Locals live in a fast array indexed by position (`LOAD_FAST`), globals and builtins are looked up by name (`LOAD_GLOBAL`), and attributes by name on the object (`LOAD_ATTR`). This is why caching a global or method in a local inside a hot loop can help: it replaces a dictionary lookup with an array read.

### Code objects and frames

A **code object** is the immutable compiled form: it holds the bytecode plus `co_consts`, `co_names` (global and attribute names), `co_varnames` (locals), `co_freevars` and `co_cellvars` (closures), and flags such as "is a generator". A function object wraps a code object together with its globals, defaults and closure. A **frame** is the per-call execution record: instruction pointer, the locals array, the value stack, and a link to the caller.

```python
import sys

c = add.__code__
print(c.co_varnames, c.co_consts, c.co_names, c.co_argcount)

def inner():
    f = sys._getframe()
    return f.f_code.co_name, f.f_back.f_code.co_name

def outer():
    z = 5
    return inner()

print(outer())
```

```text
('a', 'b') (None,) () 2
('inner', 'outer')
```

The frame also exposes `f_lineno` and `f_locals`. Since 3.11, calls to Python functions run in cheap interpreter frames inside a contiguous stack, and a full `frame` object is created lazily only when something such as a traceback, a debugger or `sys._getframe` asks for it. Exceptions are also cheaper: the `try` block itself has zero runtime cost on the non-exceptional path. Practical consequences: a stored traceback or exception keeps every frame (and all their locals) on the stack alive, which is a classic memory-retention bug. A generator keeps its frame in `gen.gi_frame` until it finishes, then sets it to `None`. In 3.13, `frame.f_locals` for functions returns a write-through proxy (PEP 667) rather than a stale snapshot.

> **Pitfall:** Storing `sys.exc_info()` or an exception object in a long-lived structure pins the traceback and its frames. Extract what you need (message, type, `traceback.format_exception` text) and drop the object.

### The specializing adaptive interpreter

Python 3.11 (PEP 659) added **quickening**: a function's bytecode starts generic, and after a short warm-up the interpreter rewrites hot instructions into **specialized** forms backed by inline caches. `BINARY_OP` becomes `BINARY_OP_ADD_INT` once it has seen two ints, `LOAD_ATTR` becomes `LOAD_ATTR_INSTANCE_VALUE` for a stable instance layout, and `LOAD_GLOBAL` caches the dictionary version. If the types change, the instruction **deoptimizes** and may re-specialize. You can observe this with `dis(..., adaptive=True)`:

```python
import dis

def add(a, b):
    return a + b

for _ in range(2000):
    add(1, 2)
dis.dis(add, adaptive=True)        # BINARY_OP_ADD_INT

for _ in range(2000):
    add("a", "b")
dis.dis(add, adaptive=True)        # BINARY_OP_ADD_UNICODE
```

```text
  3           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP_ADD_INT        0 (+)
              RETURN_VALUE
  3           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP_ADD_UNICODE    0 (+)
              RETURN_VALUE
```

(`RESUME` lines omitted; in 3.13 they appear as `RESUME_CHECK` once specialized.) The takeaway is that monomorphic hot code, where the same operation always sees the same types and object layouts, is faster, and type-unstable code keeps paying for deoptimization. This is part of why "write boring, consistent Python" is performance advice. CPython 3.13 also ships an experimental JIT (PEP 744), compiled in only with a build flag and off by default; do not assume it in production.

### The GIL: what it protects and what it does not

The **global interpreter lock** is a mutex that lets only one thread execute Python bytecode at a time within one interpreter. It exists because CPython's reference counts, allocator and many internal structures are not thread-safe; the lock makes the C-level state consistent and C extensions simpler. It is **released** during blocking I/O (sockets, files, `time.sleep`) and by C extensions that choose to release it (NumPy, many compression and crypto routines), which is why threads help I/O-bound and some numeric work but not pure-Python CPU work.

A running thread is asked to give up the lock when another thread has waited longer than the **switch interval** (`sys.getswitchinterval()`, default 5 ms). The request sets a flag that the evaluation loop checks at specific points (such as calls and backward jumps), so a switch is cooperative at the bytecode level, not arbitrary.

```python
import sys, threading, time

def burn(n=3_000_000):
    x = 0
    for i in range(n):
        x += i
    return x

t = time.perf_counter(); burn(); burn(); sequential = time.perf_counter() - t

t = time.perf_counter()
threads = [threading.Thread(target=burn) for _ in range(2)]
for th in threads: th.start()
for th in threads: th.join()
threaded = time.perf_counter() - t

print(sys.getswitchinterval(), sequential / threaded)   # ratio is about 1.0 or below on a GIL build
```

On a normal (GIL) build the ratio hovers around 1.0 or lower, because two CPU-bound threads simply take turns, plus lock handoff overhead. A typical run on 3.13 gives roughly 0.8.

> **Pitfall:** The GIL does not make your code thread-safe. It makes single bytecodes safe, but `n += 1` compiles to a load, an add and a store (`LOAD_GLOBAL`, `LOAD_CONST`, `BINARY_OP`, `STORE_GLOBAL`), and a switch can fall between them. Whether you see lost updates in practice depends on the version and the operands, which is exactly why the bug survives testing. Protect shared state with `threading.Lock`, a `queue.Queue`, or by avoiding sharing.

```python
import threading

lock = threading.Lock()
counter = 0

def inc(times: int) -> None:
    global counter
    for _ in range(times):
        with lock:
            counter += 1

threads = [threading.Thread(target=inc, args=(100_000,)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)
```

```text
400000
```

### Free-threaded CPython (PEP 703, build 3.13t)

Python 3.13 introduced an optional **free-threaded** build (`python3.13t`) with no GIL, so threads can run Python code on multiple cores. In 3.13 it is experimental; 3.14 treats it as officially supported (PEP 779) while still optional. Check what you are running with `sys._is_gil_enabled()` and `sysconfig.get_config_var("Py_GIL_DISABLED")`; the environment variable `PYTHON_GIL=1` forces the lock back on.

Removing the lock required changing the runtime, not just deleting a mutex. Reference counting became **biased** (cheap non-atomic updates by the owning thread, atomic ones from others), common objects are immortal, the allocator switched to mimalloc, and built-in containers use fine-grained per-object locks so a concurrent `list.append` cannot corrupt the list. The costs: a single-thread slowdown in 3.13 (reduced in later releases), larger memory use, and C extensions that must be rebuilt and declare they are safe without the GIL, otherwise importing one re-enables the GIL (with a warning). What does **not** change: compound operations such as check-then-set remain races, so you still need locks. It is not a drop-in `multiprocessing` replacement yet; benchmark with your dependencies.

### Subinterpreters (PEP 684 and PEP 734)

A **subinterpreter** is an isolated Python runtime within the same process, with its own modules and globals. Since 3.12 (PEP 684) each can have its **own GIL**, so several interpreters can run Python bytecode in parallel in one process. PEP 734 adds a standard-library API, `concurrent.interpreters`, with an `InterpreterPoolExecutor` in `concurrent.futures`, in Python 3.14. Objects are not shared between interpreters; data is copied or passed over queues and channels, and only some types can be shared. Startup is cheaper than a new process and memory sharing is better, but isolation is stricter than threads, and extension modules must support multi-phase initialization to be usable.

| Workload | Reasonable choice |
|---|---|
| I/O-bound, many connections | `asyncio` or threads (the GIL is released while waiting) |
| CPU-bound pure Python, mature deps | `multiprocessing` / `ProcessPoolExecutor` |
| CPU-bound in C-extensions that release the GIL (NumPy) | Threads |
| CPU-bound, shared in-memory state, willing to test | Free-threaded 3.13t or newer |
| CPU-bound, isolated tasks, 3.14+ | Subinterpreter pool |

## Practical Backend Scenario

A document-ingestion service tokenizes PDFs in a `ThreadPoolExecutor` with 16 workers on a 16-core box. CPU stays at 100% of a single core and throughput does not improve past two workers, because the tokenizer is pure Python and the threads contend for the GIL. Profiling shows I/O is a minor share. Options are evaluated in order: move the tokenizer to a process pool (works today, costs serialization), use a C-backed tokenizer that releases the GIL, or trial the free-threaded build in a canary after checking that every dependency (including the PDF parser) advertises free-threaded support. In the canary, a hidden check-then-set race in a shared cache, which the GIL used to mask in practice, starts corrupting counts, so the team adds a lock around the cache first.

## Practice Loop

1. Disassemble a function with a loop and a global lookup, then rewrite it to bind the global and a method to locals and compare the `LOAD_GLOBAL`/`LOAD_ATTR` counts and a `timeit` measurement.
2. Run the specialization demo with `adaptive=True` and watch the opcodes change when you switch from ints to strings.
3. Use `sys._getframe()` and `f_back` to build a tiny `caller_name()` helper, then show with a generator that `gi_frame` is `None` after exhaustion.
4. Run the CPU-bound two-thread benchmark and record the ratio; then run it with `ProcessPoolExecutor` and compare.
5. Write an unsynchronized shared counter with four threads, run it many times, and add a lock. Explain why you may not see the bug.
6. Print `sys.getswitchinterval()`, change it, and describe what would change for latency and throughput.
7. If you can install `python3.13t`, run the same benchmark and report `sys._is_gil_enabled()` and the speedup.

## Evidence of Understanding

- I can read a short `dis` listing and explain which opcodes do name lookups, calls and arithmetic.
- I can explain what a code object, a function object and a frame each hold, and why tracebacks can retain memory.
- I can describe how the specializing interpreter works and why type-stable code is faster.
- I can state precisely what the GIL protects, when it is released, and why `n += 1` is still a race.
- I can summarize what changes in free-threaded builds, and what does not.
- I can compare threads, processes, free-threading and subinterpreters for a workload and justify the pick.

## Interview Questions to Rehearse

### Q: What does CPython do between `python script.py` and your code running?

It compiles the source to an AST and then to bytecode inside code objects, caching imported modules as `.pyc`. The evaluation loop then executes bytecode instructions on a value stack, one frame per active call. Since 3.11, hot instructions are specialized in place using inline caches.

### Q: What does the GIL actually guarantee?

It guarantees that only one thread runs Python bytecode at a time in one interpreter, which keeps CPython's internal state consistent. It does not make compound operations atomic: a thread can be preempted between the load and the store of `n += 1`. The lock is released around blocking I/O and by C code that opts in, so threads help I/O-bound work but not pure-Python CPU work.

### Q: Why can `sys.setswitchinterval` matter, and when would you change it?

The interval controls how long a waiting thread waits before asking the running one to release the GIL. A lower value improves latency for threads that need to run quickly, at the cost of more switching overhead. In most services it is left alone; changing it is a tuning knob for specific latency-versus-throughput problems, and it does not give CPU parallelism.

### Q: What changes in the free-threaded 3.13t build?

There is no GIL, so threads run Python code in parallel. To make that safe the runtime uses biased reference counting, immortal objects, per-object locks for built-in containers and a different allocator. Single-thread performance is somewhat lower in 3.13, and C extensions must be built and declared safe without the GIL or the lock is re-enabled. User code still needs locks for compound operations.

### Q: How do subinterpreters differ from threads and processes?

They are isolated interpreters in one process, each with its own modules and (since 3.12) its own GIL, so they can run in parallel without free-threading. They share no Python objects; communication goes through queues or channels. They cost less than processes and are isolated like them, but extension support is the limiting factor. PEP 734 adds the standard-library API in 3.14.

### Q: Why is a global lookup slower than a local lookup, and does it matter?

Locals are indexed in an array (`LOAD_FAST`), while globals and builtins require dictionary lookups, partially mitigated by inline caches in 3.11+. It rarely matters outside very hot loops; measure first. Binding to a local is a micro-optimization worth knowing, not a default style.

## Common Pitfalls

- Believing the GIL makes `+=`, check-then-set or dictionary read-modify-write sequences atomic.
- Using a thread pool for CPU-bound pure-Python work and expecting a speed-up.
- Depending on opcode names or bytecode layout in tools, since they change across minor versions.
- Keeping exceptions or tracebacks in long-lived objects, which retains whole frames.
- Benchmarking before warm-up, or with unstable types, and misreading specialization effects.
- Assuming the free-threaded build is a drop-in upgrade: dependencies may re-enable the GIL or not work.
- Passing unpicklable or large objects to process pools and blaming Python instead of serialization cost.

## Suggested Extension

Write a micro-benchmark harness that runs a CPU-bound function under four strategies (sequential, `ThreadPoolExecutor`, `ProcessPoolExecutor`, and on 3.14 an interpreter pool or on 3.13t plain threads) at 1, 2, 4 and 8 workers, prints a table of throughput and peak memory, and records `sys.version`, `sys._is_gil_enabled()` and the switch interval alongside the results. Explain the shape of each curve.
