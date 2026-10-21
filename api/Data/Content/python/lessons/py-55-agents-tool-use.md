# Agents, Tool Use and Orchestration

An agent is a loop in which a language model decides what to do next, your code does it, and the result goes back to the model. That loop is easy to write and hard to operate: it can call tools that do not exist, repeat itself forever, burn a month of budget in an afternoon, or take an irreversible action on a model's whim. Interviewers use agents to test whether you treat the model as an unreliable component inside a deterministic system, which means step limits, budgets, validation, durable state and human approval.

## Concepts Covered

### The agent loop: think, act, observe

Strip away frameworks and an agent is a bounded `for` loop. Each iteration sends the conversation so far to the model (think). The model replies either with a final answer or with a request to call a tool. If it asks for a tool, your code validates and executes it (act), appends the result as a tool message (observe), and loops. Everything that makes it production-grade is a guard around that loop: a maximum number of steps, a token or cost budget, detection of repeated calls, per-tool timeouts and an approval gate for risky tools.

The code below defines the protocol between loop and model, a tool registry whose arguments are validated with Pydantic, and the loop itself. The message dictionaries are generic and illustrative: real providers differ in how they represent tool calls, so isolate that difference inside the `Model` adapter.

```python
from __future__ import annotations

import asyncio
import json
from collections import Counter
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: str                    # JSON text, exactly as the model produced it


@dataclass(frozen=True, slots=True)
class ModelReply:
    text: str | None = None           # final answer when tool_call is None
    tool_call: ToolCall | None = None
    tokens: int = 0


class Model(Protocol):
    async def next(self, messages: list[dict]) -> ModelReply: ...
```

### A tool registry with validated arguments

Tools are described to the model by a name, a description and a JSON Schema (generated from the Pydantic model, as in the previous lesson). When the model calls one, the registry resolves the name, validates the arguments, enforces approval for risky tools and applies a timeout. The most important design decision is that **failures become observations, not exceptions**: an unknown tool, bad arguments or a timeout returns an `ERROR ...` string the model can read and recover from, while the loop itself never crashes. The error text should help (list the available tools, name the invalid field) but never leak secrets or stack traces.

```python
Handler = Callable[[BaseModel], Awaitable[str]]
Approver = Callable[[ToolCall], bool]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    args: type[BaseModel]
    handler: Handler
    timeout_s: float = 5.0
    needs_approval: bool = False


class Registry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def tool(self, name: str, args: type[BaseModel], *, timeout_s: float = 5.0,
             needs_approval: bool = False) -> Callable[[Handler], Handler]:
        def register(fn: Handler) -> Handler:
            self._tools[name] = ToolSpec(name, args, fn, timeout_s, needs_approval)
            return fn
        return register

    async def run(self, call: ToolCall, approve: Approver) -> str:
        """Always returns an observation string; failures are data for the model, not crashes."""
        spec = self._tools.get(call.name)
        if spec is None:
            return f"ERROR unknown tool {call.name!r}. Available: {', '.join(sorted(self._tools))}"
        try:
            args = spec.args.model_validate_json(call.arguments)
        except ValidationError as exc:
            first = exc.errors(include_url=False)[0]
            return f"ERROR invalid arguments at {'.'.join(map(str, first['loc']))}: {first['msg']}"
        if spec.needs_approval and not approve(call):
            return "ERROR denied: a human reviewer did not approve this action"
        try:
            async with asyncio.timeout(spec.timeout_s):
                return await spec.handler(args)
        except TimeoutError:
            return f"ERROR tool {call.name!r} timed out after {spec.timeout_s}s"
        except Exception as exc:                                  # boundary: keep the loop alive
            return f"ERROR tool {call.name!r} failed ({type(exc).__name__})"
```

### The guarded loop

```python
StopReason = Literal["final", "max_steps", "budget", "loop"]


@dataclass(slots=True)
class RunResult:
    answer: str | None
    stop_reason: StopReason
    steps: int
    tokens: int
    trace: list[str]


async def run_agent(model: Model, registry: Registry, question: str, *, max_steps: int = 6,
                    token_budget: int = 2000, max_repeats: int = 2,
                    approve: Approver = lambda call: False) -> RunResult:
    messages: list[dict] = [{"role": "system", "content": "Use tools when needed."},
                            {"role": "user", "content": question}]
    seen: Counter[tuple[str, str]] = Counter()
    tokens, trace = 0, []
    for step in range(1, max_steps + 1):
        reply = await model.next(messages)                        # think
        tokens += reply.tokens
        if tokens > token_budget:
            return RunResult(None, "budget", step, tokens, trace)
        call = reply.tool_call
        if call is None:
            return RunResult(reply.text, "final", step, tokens, trace)
        seen[(call.name, call.arguments)] += 1
        if seen[(call.name, call.arguments)] > max_repeats:
            return RunResult(None, "loop", step, tokens, trace)
        observation = await registry.run(call, approve)           # act
        trace.append(f"{step}. {call.name}({call.arguments}) -> {observation}")
        messages += [{"role": "assistant", "content": None,       # observe
                      "tool_call": {"id": call.id, "name": call.name, "arguments": call.arguments}},
                     {"role": "tool", "tool_call_id": call.id, "content": observation}]
    return RunResult(None, "max_steps", max_steps, tokens, trace)
```

Notice the order inside one iteration: the budget is checked *before* the tool runs, so an over-budget reply does not cause a side effect. The `Approver` defaults to denying everything, which is the safe default for an unconfigured agent.

I ran this against a scripted fake model (`get_order` is a read tool, `refund` needs approval, `slow_lookup` has a 50 ms timeout) and got these outcomes:

- **Happy path:** one `get_order` call, then a final answer; `stop=final steps=2 tokens=200`.
- **Hallucinated tool:** `delete_database` returns `ERROR unknown tool 'delete_database'. Available: get_order, refund, slow_lookup`; the model recovers on the next step and finishes (3 steps).
- **Bad arguments:** order id `A1B2` returns `ERROR invalid arguments at order_id: String should match pattern '^ord_[a-z0-9]{4}$'`.
- **Approval:** with the default approver the refund returns `ERROR denied: a human reviewer did not approve this action`; with an approving callback it returns `refunded 20.00 on ord_a1b2`.
- **Timeout:** `slow_lookup` returns `ERROR tool 'slow_lookup' timed out after 0.05s`.
- **Repeating itself:** the same call four times ends with `stop=loop steps=3` (the third identical call is refused).
- **Over budget:** three 900-token replies against a 2,000 budget end with `stop=budget steps=3 tokens=2700`.
- **Max steps:** an endless sequence of distinct calls ends with `stop=max_steps steps=3` when `max_steps=3`.

> **Pitfall:** Loop detection that compares raw argument strings misses a model that varies whitespace or key order. Canonicalise (parse and re-serialise with sorted keys) before counting, and also cap total calls per tool.

### State and memory

Three kinds of state exist, and mixing them up causes bugs. **Run state** is everything the current run needs: messages, step count, budget spent, scratchpad. **Short-term memory** is the conversation history, which grows with every step and must be trimmed or summarised to fit the context window and the cost target. **Long-term memory** is anything persisted across runs (user preferences, past tickets), typically retrieved on demand with the RAG techniques from the previous lesson rather than stuffed into every prompt.

When trimming history, preserve structure: keep the system prompt, keep the newest messages that fit, and never begin the kept tail with a tool result whose originating assistant message was dropped, because providers reject orphaned tool results.

```python
def trim_messages(messages: list[dict], max_chars: int) -> list[dict]:
    """Keep the system prompt plus the newest messages that fit; never start on an orphaned tool result."""
    system, rest = messages[:1], messages[1:]
    kept: list[dict] = []
    size = len(system[0]["content"] or "")
    for m in reversed(rest):
        cost = len(str(m.get("content") or "")) + len(str(m.get("tool_call") or ""))
        if size + cost > max_chars:
            break
        kept.append(m)
        size += cost
    kept.reverse()
    while kept and kept[0]["role"] == "tool":
        kept.pop(0)
    return system + kept
```

For a history of `system, user, assistant(call), tool, assistant(call), tool` with a budget of 1,000 characters, every role survives; with a budget of 80 only `['system', 'assistant', 'tool']` remain, the newest call and its result. In production, prefer summarising dropped turns into a short note over silently forgetting them, and count tokens rather than characters.

### Graph orchestration

A single loop is fine for open-ended tasks. For workflows with known structure (classify, draft, review, execute) an explicit graph is easier to test, resume and audit. The vocabulary, as used by LangGraph and similar frameworks:

- **State:** a typed object shared by all nodes.
- **Nodes:** functions that take the state and return a *partial update*.
- **Edges:** static edges name the next node; **conditional edges** call a router function on the state to choose.
- **Reducers:** per-key merge functions. Without one a new value overwrites the old; with `operator.add` on a list, updates append, which is how parallel or sequential nodes contribute to one log or message list.
- **Checkpoints:** the state is saved after each step under a thread id, which gives you crash recovery, resumability, time travel for debugging, and the basis for human-in-the-loop pauses.

To make this concrete without a dependency, here is a minimal graph runner that shows the mechanics.

```python
import copy
import operator
from dataclasses import dataclass

END = "__end__"
State = dict[str, object]
Update = dict[str, object]
Node = Callable[[State], Update]
Router = Callable[[State], str]
Reducer = Callable[[object, object], object]


@dataclass(frozen=True, slots=True)
class Checkpoint:
    state: State
    next_node: str | None          # None means the run finished


class MiniGraph:
    def __init__(self, reducers: dict[str, Reducer] | None = None,
                 store: dict[str, Checkpoint] | None = None) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, str | Router] = {}
        self._reducers = reducers or {}
        self.store = store if store is not None else {}      # stand-in for a durable checkpointer

    def add_node(self, name: str, fn: Node) -> None:
        self._nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        self._edges[src] = dst

    def add_conditional_edges(self, src: str, router: Router) -> None:
        self._edges[src] = router

    def _merge(self, state: State, update: Update) -> State:
        merged = dict(state)
        for key, value in update.items():
            reducer = self._reducers.get(key)
            merged[key] = reducer(state.get(key), value) if reducer else value
        return merged

    def _run(self, thread: str, state: State, node: str | None, interrupt_before: frozenset[str],
             skip_interrupt_once: bool) -> Checkpoint:
        while node is not None and node != END:
            if node in interrupt_before and not skip_interrupt_once:
                cp = Checkpoint(copy.deepcopy(state), node)    # paused: waiting for a human
                self.store[thread] = cp
                return cp
            skip_interrupt_once = False
            state = self._merge(state, self._nodes[node](copy.deepcopy(state)))
            edge = self._edges[node]
            node = edge(state) if callable(edge) else edge
            self.store[thread] = Checkpoint(copy.deepcopy(state), None if node == END else node)
        return self.store[thread]

    def start(self, thread: str, initial: State, entry: str,
              interrupt_before: frozenset[str] = frozenset()) -> Checkpoint:
        return self._run(thread, initial, entry, interrupt_before, False)

    def resume(self, thread: str, update: Update | None = None,
               interrupt_before: frozenset[str] = frozenset()) -> Checkpoint:
        cp = self.store[thread]
        if cp.next_node is None:
            return cp
        state = self._merge(cp.state, update or {})
        return self._run(thread, state, cp.next_node, interrupt_before, True)
```

A refund workflow built on it: `classify` routes refund requests to `draft_refund`, which flows into `execute_refund`, then `reply`. The graph is told to pause before `execute_refund`, and the `log` key uses `operator.add` as its reducer.

```python
def classify(s: State) -> Update:
    refund = "refund" in str(s["question"]).lower()
    return {"category": "refund" if refund else "other", "log": ["classify"]}

def draft_refund(s: State) -> Update:
    return {"amount": 20.0, "log": ["draft_refund"]}

def execute_refund(s: State) -> Update:
    if not s.get("approved"):
        return {"result": "refund rejected", "log": ["execute_refund(rejected)"]}
    return {"result": f"refunded {s['amount']:.2f}", "log": ["execute_refund"]}

def reply(s: State) -> Update:
    return {"log": ["reply"]}

def build(store=None) -> MiniGraph:
    g = MiniGraph(reducers={"log": operator.add}, store=store)      # 'log' appends; others overwrite
    g.add_node("classify", classify)
    g.add_node("draft_refund", draft_refund)
    g.add_node("execute_refund", execute_refund)
    g.add_node("reply", reply)
    g.add_conditional_edges("classify", lambda s: "draft_refund" if s["category"] == "refund" else "reply")
    g.add_edge("draft_refund", "execute_refund")
    g.add_edge("execute_refund", "reply")
    g.add_edge("reply", END)
    return g

GATE = frozenset({"execute_refund"})
shared_store: dict = {}
cp = build(shared_store).start("t1", {"question": "Please refund my order", "log": []}, "classify",
                               interrupt_before=GATE)
print("paused before:", cp.next_node, "| log:", cp.state["log"])
done = build(shared_store).resume("t1", {"approved": True}, interrupt_before=GATE)   # a "new process"
print("finished:", done.next_node is None, "|", done.state["result"], "| log:", done.state["log"])
```

```text
paused before: execute_refund | log: ['classify', 'draft_refund']
finished: True | refunded 20.00 | log: ['classify', 'draft_refund', 'execute_refund', 'reply']
```

The second graph object is a fresh instance that shares only the checkpoint store, which models resuming in another process after a crash or a day-long human delay. Resuming with `{"approved": False}` ends with `refund rejected` and a log ending `execute_refund(rejected)`, `reply`; a question that is not about refunds goes `classify`, `reply` and never reaches the gate.

In real LangGraph (illustrative; check the current documentation for exact signatures) the same ideas read like this: `builder = StateGraph(State)` with a `TypedDict` state whose list fields are annotated `Annotated[list[str], operator.add]` to declare a reducer, `builder.add_node("classify", classify)`, `builder.add_edge(START, "classify")`, `builder.add_conditional_edges("classify", route)`, `graph = builder.compile(checkpointer=...)`, and `graph.invoke(inputs, config={"configurable": {"thread_id": "t1"}})`. Human approval uses its interrupt mechanism (for example `interrupt_before` at compile time, or an `interrupt` call inside a node) together with a checkpointer, and resuming continues from the saved state. The decision of loop versus graph is a design trade-off: loops give flexibility, graphs give determinism, testability and auditability.

### Human-in-the-loop and guardrails

Guardrails are layered. **Before the model:** validate and size-limit user input, strip or label untrusted content. **Around tools:** a per-agent allowlist, schemas with strict validation, timeouts, least-privilege credentials, idempotency keys on side effects, and an approval gate on anything irreversible or costly (refunds, deletions, outbound email). **After the model:** validate the final answer's structure, redact secrets and personal data, check citations when grounding is required. Approval must be a property of the *tool*, enforced in code, rather than a prompt instruction the model could ignore.

### Failure modes to design against

- **Infinite or oscillating loops:** same call repeatedly, or A then B then A. Counters, a step limit and a "no progress" check on state.
- **Hallucinated tools or arguments:** answer with a useful error and the list of valid tools, and count occurrences; a spike indicates a prompt or schema regression.
- **Runaway cost:** a budget in tokens, dollars and wall-clock time, enforced per run and per tenant, with an alert on p99 cost per task.
- **Context bloat:** unbounded history makes every step slower and more expensive, and degrades quality; trim, summarise, or reset.
- **Compounding errors:** a small mistake in step 2 poisons step 6. Keep tasks short, verify intermediate results with deterministic checks, and prefer a graph for long workflows.
- **Non-idempotent side effects on retry:** a resumed run must not charge twice, so tool calls carry idempotency keys derived from run id and step.
- **Prompt injection through tool output:** treat results as data and keep tool scopes minimal, as covered in the structured-output lesson.

> **Interview tip:** When asked to design an agent, lead with the constraints (max steps, budget, allowlisted tools, approvals, checkpointed state, evaluation set of tasks) before talking about prompts. It shows you build systems, not demos.

## Practical Backend Scenario

A support team wants an agent that investigates delayed orders: look up the order, check carrier status, draft a customer reply and, when warranted, propose a refund. The first prototype was a free-running loop with six tools and no limits. In week one it looped on a flaky carrier API (400 calls on one ticket), invented a `check_warehouse` tool and then kept retrying it, and once issued a duplicate refund after a retry. The rebuild splits the work into a graph: a read-only investigation loop capped at six steps and 30 cents, a deterministic `draft_reply` node, and a refund node behind an approval interrupt with an idempotency key. State is checkpointed per ticket, so an agent waiting for an approver survives a deploy, and a replay of 200 historical tickets runs in CI to catch regressions.

## Practice Loop

1. Implement `Registry` and `run_agent` with a scripted fake model. Reproduce all eight outcomes above in tests: happy path, hallucinated tool, bad arguments, denied and approved refunds, timeout, loop, budget and max steps.
2. Canonicalise tool arguments (sorted-key JSON) before loop detection and add a test where the model varies whitespace.
3. Add a per-tool call cap and a wall-clock deadline using `asyncio.timeout` around the entire run.
4. Write `trim_messages` and test that it never returns a leading tool message.
5. Build `MiniGraph`, wire the refund workflow, and test pause, resume from a second instance, and the rejected path.
6. Add idempotency keys to the refund tool (derived from thread id and step) and test that resuming twice does not refund twice.

## Evidence of Understanding

- I can draw the think, act, observe loop and name the five guards I put around it.
- I can explain why tool errors are returned as observations and what the error text should contain.
- I can distinguish run state, short-term memory and long-term memory and say how each is bounded.
- I can describe nodes, edges, conditional edges, reducers and checkpoints, and how checkpoints enable human-in-the-loop and crash recovery.
- I can list at least five agent failure modes with one concrete mitigation each.
- I can argue when to prefer a graph to a free-running loop.

## Interview Questions to Rehearse

### Q: How do you stop an agent from running away?
Several independent limits: a maximum step count, a token or dollar budget checked before each tool executes, a wall-clock deadline, a cap on repeated identical calls, and per-tool timeouts. When any limit trips, the run ends with an explicit stop reason that is logged and surfaced, rather than silently truncating.

### Q: The model calls a tool that does not exist. What happens?
The registry returns an error observation naming the available tools, the loop continues, and the model usually self-corrects. I count these events as a metric, because a rise points to a prompt, schema or model regression. I never map unknown names to a "closest" tool, since a wrong guess can be a harmful action.

### Q: When would you use a graph framework instead of a plain loop?
When the workflow has known stages, needs deterministic routing, must survive restarts or long human delays, or must be audited step by step. Checkpointing gives resumability and debugging by replay. For open-ended exploration within a tight sandbox, a bounded loop is simpler and more flexible.

### Q: How do you add human approval safely?
Approval is a property of the tool, enforced in code. The tool call is validated, then execution pauses and the pending call, with its arguments and context, is stored in a checkpoint. A reviewer approves or rejects through an authenticated path, and the run resumes with that decision. The side effect carries an idempotency key so a retry cannot duplicate it, and the decision is logged.

### Q: How do you test an agent?
Unit-test the registry and guards deterministically with a scripted fake model, including the failure modes. Then keep an evaluation set of real tasks with expected tool sequences or outcomes, run it in CI against a pinned model and prompt, and track success rate, step count, cost and stop reasons per version. Live-model tests are statistical, so compare distributions, not single runs.

## Common Pitfalls

- A `while True` loop with no step, budget or time limit.
- Raising exceptions from tools so one bad call kills the run, instead of returning an observation.
- Letting the prompt, not the code, decide which tools need approval.
- Loop detection on raw argument strings, defeated by key order and whitespace.
- Unbounded message history, which inflates cost and degrades answers.
- Dropping a tool-call message while keeping its tool result, which providers reject.
- Side-effecting tools without idempotency keys, duplicated by retries or resumed runs.
- Checkpointing only at the end of a run, so a crash loses everything.
- Treating tool output as trusted instructions.
- Evaluating by eyeballing a few chats instead of replaying a task set.

## Suggested Extension

Add a supervisor-and-worker pattern to the graph: a router node that classifies a ticket and dispatches to one of two sub-graphs (investigate, refund), each with its own tools and budget, with results merged through a reducer. Add a "reflection" node that checks the draft reply against the retrieved order data and sends it back for one revision at most, and measure on a replay set whether the extra step improves outcomes enough to justify its cost.
