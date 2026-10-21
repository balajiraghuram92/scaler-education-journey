# The Senior Python Interview Playbook

A 45-minute Python round is rarely about whether you can solve the puzzle. It is about whether you work like a senior engineer: you clarify before coding, you write idiomatic and readable Python, you reason about complexity out loud, you notice the traps that bite in production, and you test your own work. Candidates who know the language but skip the process still get "no hire" notes. This lesson is the checklist to rehearse until it is automatic.

## Concepts Covered

### Idioms interviewers look for

The code you write in the first minutes signals your seniority. Prefer constructs that say what you mean:

- A **comprehension** for building a list, set or dict from an iterable with at most one condition; a plain loop once it needs side effects, multiple branches or nested conditions. A generator expression when you only iterate once (`sum(x * x for x in xs)`).
- `enumerate(xs, start=1)` instead of `range(len(xs))`, `zip(a, b)` to walk sequences together (`zip(..., strict=True)` on 3.10+ when lengths must match), and `dict.items()` instead of indexing.
- **Unpacking** for swaps, tuple returns and head/tail splits: `first, *middle, last = xs`.
- **Context managers** (`with`) for anything that must be released: files, locks, DB sessions, timers. Write your own with `contextlib.contextmanager` and put cleanup in `finally`.
- **Generators** (`yield`) to stream or batch lazily rather than materialising everything; remember a generator is single-pass.

```python
from collections.abc import Iterator

rows = [("acme", 120), ("globex", 0), ("initech", 45), ("umbrella", 300)]

# loop-and-index style
out = []
for i in range(len(rows)):
    if rows[i][1] > 0:
        out.append(rows[i][0].upper() + ":" + str(rows[i][1]))

# idiomatic
out2 = [f"{name.upper()}:{tokens}" for name, tokens in rows if tokens > 0]
print(out == out2, out2)

for i, (name, tokens) in enumerate(rows, start=1):
    if i == 2:
        print(i, name, tokens)

names, counts = zip(*rows)
first, *middle, last = [1, 2, 3, 4, 5]
print(names, counts)
print(first, middle, last)


def read_chunks(lines: list[str], size: int) -> Iterator[list[str]]:
    chunk: list[str] = []
    for line in lines:
        chunk.append(line)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


print(list(read_chunks(list("abcde"), 2)))
gen = (x * x for x in range(5))
print(sum(gen), sum(gen))
```

```text
True ['ACME:120', 'INITECH:45', 'UMBRELLA:300']
2 globex 0
('acme', 'globex', 'initech', 'umbrella') (120, 0, 45, 300)
1 [2, 3, 4] 5
[['a', 'b'], ['c', 'd'], ['e']]
30 0
```

The last line is a favourite interview trap: the second `sum(gen)` is `0` because the generator is exhausted by the first one.

### Live-coding discipline

Process beats speed. A reliable 45-minute shape:

1. **Minutes 0-5, clarify.** Restate the problem, ask about input size, duplicates, empty input, ordering and tie-breaking, and what to return on invalid input. Write down two or three examples.
2. **Minutes 5-10, approach.** State the brute force and its complexity first, then the improvement and why. Name the data structures (`Counter`, `heapq`, `set`, `deque`) and agree on the approach before typing.
3. **Minutes 10-30, code.** Small functions, clear names, type hints on signatures, no premature cleverness. Narrate decisions: "I'll break ties alphabetically so output is deterministic."
4. **Minutes 30-38, verify.** Trace your own examples by hand, then edge cases: empty, single element, duplicates, large input, invalid input. Write two or three `assert` statements in the editor.
5. **Minutes 38-45, extend.** State complexity, discuss what changes at scale (streaming, memory, concurrency), and what you would test or monitor in production.

Here is a solution shaped by that process: the top-k most frequent tokens, with a deterministic tie-break and an `O(n log k)` selection instead of sorting everything.

```python
import heapq
import re
from collections import Counter


def top_k_tokens(text: str, k: int) -> list[tuple[str, int]]:
    """Most frequent tokens; ties broken alphabetically so output is deterministic."""
    counts = Counter(re.findall(r"[a-z0-9']+", text.lower()))
    return heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))


text = "the cat and The dog and the bird. And a cat!"
print(top_k_tokens(text, 3))
print(top_k_tokens("", 3))
print(top_k_tokens("a b", 5))
```

```text
[('and', 3), ('the', 3), ('cat', 2)]
[]
[('a', 1), ('b', 1)]
```

### Complexity talk

Quote complexity with the right vocabulary and the assumption behind it. Dict and set lookups and inserts are average `O(1)` (worst case `O(n)` with pathological collisions). `list.append` is amortised `O(1)`; `x in a_list`, `list.remove` and `list.insert(0, x)` are `O(n)`, so use a `set` for membership and a `collections.deque` for queues. `sorted` is Timsort: `O(n log n)` worst case, close to `O(n)` on partly sorted data, and **stable**. `heapq.nlargest/nsmallest(k, ...)` is about `O(n log k)`. Slicing copies, so repeated slicing in a loop is quadratic; building a string with `"".join(parts)` beats repeated `+=`. Always separate time from space, and say what `n` is. If you cannot beat `O(n^2)`, say so, say why, and ask whether the input size makes it acceptable.

### Common traps

These come up because they cause real production bugs. Run them and be ready to explain each one.

```python
def add(item, bucket=[]):          # default list is created once, at definition
    bucket.append(item)
    return bucket

print(add(1), add(2))

fs = [lambda: i for i in range(3)]          # closures capture the variable, not the value
print([f() for f in fs])
fs = [lambda i=i: i for i in range(3)]      # bind the value at definition time
print([f() for f in fs])

a = int("257")
b = int("257")
print(a == b, a is b)                        # equal, but not the same object (CPython)

print(0.1 + 0.2 == 0.3)                      # floats: never compare with ==
import math
print(math.isclose(0.1 + 0.2, 0.3))

d1 = {"a": 1, "b": 2}
d2 = {"b": 2, "a": 1}
print(d1 == d2, list(d1) == list(d2))        # dict equality ignores order

grid = [[0] * 3] * 2                         # two references to the same row
grid[0][0] = 9
print(grid)

t = ([1], 2)
try:
    t[0] += [5]
except TypeError as e:
    print("TypeError:", e)
print(t)                                     # the mutation happened anyway

nums = [1, 2, 3, 4]
for n in nums:                               # mutating while iterating skips items
    if n % 2 == 0:
        nums.remove(n)
print(nums)
```

```text
[1, 2] [1, 2]
[2, 2, 2]
[0, 1, 2]
True False
False
True
True False
[[9, 0, 0], [9, 0, 0]]
TypeError: 'tuple' object does not support item assignment
([1, 5], 2)
[1, 3]
```

Explain them, do not just list them. The mutable default and the late-binding closure are the same idea (state captured at definition, not at call). `is` tests identity and is for `None` and other singletons only; relying on small-int caching is an implementation detail. Float equality fails because binary floating point cannot represent most decimals; use `math.isclose`, or `decimal.Decimal` for money. Dictionaries preserve insertion order (guaranteed since 3.7) but `==` ignores it, while `OrderedDict` equality is order-sensitive. Two more worth knowing: `except E as err` deletes `err` when the block ends, so using it afterwards raises `NameError`; and defining `__eq__` without `__hash__` makes a class unhashable.

> **Interview tip:** When you spot a trap in the interviewer's code, say what it does, why, and the minimal fix. Do not rewrite their whole function.

### Discussing trade-offs and testing

Frame every design choice as "X because Y, at the cost of Z": "A `Counter` keeps the code short and is `O(n)`; if the text did not fit in memory I would stream chunks and keep a bounded heap or a count-min sketch, accepting approximate counts." Cover correctness, performance, readability and operability. For tests, name categories rather than inventing them on the spot: normal case, boundaries (empty, one element, `k` larger than the number of items), duplicates and ties, invalid input, and a larger randomised or property-based check against a brute-force version. Say how you would test it with pytest (`parametrize` over a table) and what you would log or measure in production. If time is short, write the test table as comments and implement the first two.

The table below is the shape to aim for. Each case has an id, so a failure names the scenario, and I checked each expected value against the implementation above.

```python
import pytest


@pytest.mark.parametrize(
    ("text", "k", "expected"),
    [
        pytest.param("", 3, [], id="empty-text"),
        pytest.param("a b", 5, [("a", 1), ("b", 1)], id="k-larger-than-distinct"),
        pytest.param("a a b", 1, [("a", 2)], id="single-winner"),
        pytest.param("b a", 2, [("a", 1), ("b", 1)], id="tie-breaks-alphabetically"),
        pytest.param("A a!", 1, [("a", 2)], id="case-and-punctuation"),
        pytest.param("x", 0, [], id="k-zero"),
    ],
)
def test_top_k_tokens(text: str, k: int, expected: list[tuple[str, int]]) -> None:
    assert top_k_tokens(text, k) == expected
```

### Rapid-fire Q&A

Concise answers you should be able to give in ten seconds each.

| Question | Answer |
|---|---|
| `list` vs `tuple`? | Mutable vs immutable; a tuple is hashable only if all its elements are. Use tuples for fixed records and dict keys. |
| `is` vs `==`? | Identity vs equality. Use `is` for `None` and singletons only. |
| Are dicts ordered? | Insertion-ordered since 3.7 (guaranteed), but `==` ignores order. |
| What does the GIL do? | In standard CPython one thread runs Python bytecode at a time. It limits CPU-bound threading; I/O-bound threads still help. Free-threaded builds exist from 3.13 (experimental). |
| Threads, asyncio or processes? | Many I/O waits: asyncio or threads. CPU-bound: processes (or native extensions). |
| Shallow vs deep copy? | Shallow copies the container but shares the elements; `copy.deepcopy` recurses. |
| `*args` and `**kwargs`? | Collect extra positional and keyword arguments into a tuple and a dict. |
| `@staticmethod` vs `@classmethod`? | Static gets no implicit argument; class method gets the class, so it works for alternate constructors and subclasses. |
| What is a decorator? | A callable that takes a callable and returns a callable; use `functools.wraps` to keep metadata. |
| `__str__` vs `__repr__`? | `__str__` is for users, `__repr__` for developers, ideally unambiguous or `eval`-able. |
| Generator vs list? | A generator is lazy and single-pass; a list is materialised and reusable. |
| `try/except/else/finally`? | `else` runs when no exception occurred; `finally` always runs. |
| Why is `x in a_list` slow? | Linear scan, `O(n)`; a `set` or `dict` gives average `O(1)`. |
| What does `functools.lru_cache` require? | Hashable arguments; with `maxsize=None` it grows without bound. |
| `defaultdict` vs `setdefault`? | `defaultdict` calls a factory for a missing key; `setdefault` evaluates its default argument on every call. |
| What does `__slots__` do? | Replaces the per-instance `__dict__`, saving memory and blocking undeclared attributes. |
| `dataclass`, `NamedTuple`, `TypedDict`, Pydantic? | Mutable record with generated methods; immutable tuple record; typing-only dict shape; runtime validation and parsing. |
| Is `sorted` stable? | Yes; equal keys keep their input order, which enables multi-pass sorting. |
| What is the walrus operator for? | `:=` assigns inside an expression, e.g. `if (m := pattern.match(s)):`, avoiding a second call. |
| `round(2.5)`? | `2`: Python rounds halves to even (banker's rounding). |

## Practical Backend Scenario

You are in a forward-deployed engineer interview. The interviewer shares a small log-processing function for a customer's LLM gateway and asks you to "make it production-ready". It uses a mutable default argument for a cache, a list for membership checks inside a loop, `==` on floats for cost totals, and opens a file without a context manager. The strongest response follows the playbook: ask what volume and failure modes matter, name each issue with the user-visible symptom, fix them in order of risk, state the new complexity, add three focused tests, and finish with what you would monitor.

## Practice Loop

1. Time yourself solving the top-k problem from scratch in 20 minutes, speaking aloud, then rewrite it with a different tie-break rule.
2. Run every snippet in the traps section and write a one-sentence explanation for each output without looking at the lesson.
3. Pick five items from the rapid-fire table, close the lesson, and answer them aloud in ten seconds each; record yourself.
4. Take a function from your own codebase, find two idiom upgrades (comprehension, `enumerate`, context manager, generator), and note when the "upgrade" would hurt readability.
5. Do a mock round with a friend: they play interviewer and deliberately give vague requirements. Practice the clarify step.
6. For one solution, write a brute-force version and a randomised test that compares both on 1,000 random inputs.

## Evidence of Understanding

- I can run a 45-minute round with an explicit clarify, approach, code, verify and extend structure.
- I can predict and explain the output of each trap snippet, and fix each one.
- I can state the time and space complexity of common built-in operations and justify a data-structure choice.
- I can say when a comprehension, generator or plain loop is the right choice.
- I can answer the rapid-fire questions concisely and then go one level deeper when asked.

## Interview Questions to Rehearse

### Q: Walk me through how you approach a coding problem in a live interview.

I restate the problem and ask about input size, edge cases and tie-breaking, then write two examples. I state the brute force with its complexity, propose the improvement, and agree on it before coding. I write small typed functions while narrating decisions, trace my examples by hand, test edge cases, and finish with complexity, scaling and what I would test in production.

### Q: When do you choose a comprehension, a generator expression or a loop?

A comprehension when I am building a collection with a simple transform and at most one filter. A generator expression when the result is consumed once or is large, to avoid materialising it. A loop when there are side effects, several statements per element, or nested conditions where a comprehension would hurt readability.

### Q: What's wrong with `def f(x, cache={})`, and how do you fix it?

The default dict is created once when the function is defined and shared across calls, so state leaks between callers. Use `cache: dict | None = None` and create a fresh dict inside the function, or make the shared cache explicit (a module-level object or `functools.lru_cache`) when sharing is intended.

### Q: How would you test this function in the time you have?

I would pick a table of cases with names: a normal case, boundaries (empty, one item, `k` greater than the number of items), duplicates and ties, and invalid input. I would write the first few as `assert` statements, and mention a randomised comparison with a brute-force implementation and a pytest `parametrize` version for the real codebase.

### Q: Your solution is `O(n log n)`. Can you do better, and does it matter?

I would check what the bottleneck is: for top-k a heap gives `O(n log k)`, and counting is `O(n)`. Whether it matters depends on `n` and the latency budget; if the data is a stream, I would use bounded memory structures. I would measure with `timeit` or a profiler before optimising further.

### Q: What is a trade-off you made in Python and would revisit?

A good answer names a concrete choice, its cost, and the signal that would make you change it: for example, using threads plus `requests` for a quick integration, which worked until concurrency grew and the GIL and connection pool limits showed up as latency; the revisit was asyncio with `httpx`, accepting a bigger rewrite for higher concurrency and cleaner timeouts.

## Common Pitfalls

- Starting to code before clarifying requirements or stating the approach.
- Silent coding: the interviewer cannot give credit for reasoning they cannot hear.
- Over-engineering with classes and patterns when a function and a `Counter` solve it.
- Using a list for membership tests, or `list.pop(0)` as a queue.
- Mutating a collection while iterating over it.
- Comparing floats with `==`, or using `is` for value comparison.
- Skipping the verification step and handing over untested code.
- Memorised answers that collapse at the first follow-up; know the mechanism, not just the slogan.

## Suggested Extension

Record yourself doing three timed mock rounds, one each on streaming data (generator pipeline), a concurrency problem (`asyncio.gather` with a semaphore), and a caching problem (an LRU cache with `OrderedDict` or a dict plus linked list). Review the recordings for the five phases and for any trap you stepped on, and keep a personal list of questions you could not answer in ten seconds.
