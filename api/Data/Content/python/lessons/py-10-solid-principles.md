# SOLID Principles for Extensible Systems with AI Integrations

Every AI feature you ship will outlive its first model provider. Prices change, a vendor has an outage, a customer demands that data stays in one region, and suddenly the code that called one SDK directly has to call three. SOLID is the vocabulary interviewers use to ask whether your design survives that moment, and in Python the honest answer depends on knowing which principles the language enforces for you (almost none) and which it makes cheap (most of them, through `typing.Protocol` and first-class functions).

## Concepts Covered

### SRP: one reason to change, one actor to answer to

The Single Responsibility Principle is usually quoted as "a class does one thing", which is too vague to act on. The sharper formulation is that a module should have one reason to change, meaning one stakeholder whose requests can force an edit. A `RagService` that retrieves passages, assembles the prompt, calls the model, computes cost and writes the audit row has four reasons to change: the search team, the prompt author, the vendor SDK, and finance. A prompt tweak then risks breaking billing code, and you cannot unit test the prompt without a database.

The cure is to separate the parts that change for different reasons and let a thin coordinator wire them together. Notice how little ceremony Python needs: `build_prompt` stays a plain function because it has no state, while the I/O collaborators become small Protocols.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    output_tokens: int


class ChatModel(Protocol):
    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion: ...


class Retriever(Protocol):
    def search(self, query: str, k: int = 3) -> list[str]: ...


class UsageRecorder(Protocol):
    def record(self, model: str, completion: Completion) -> None: ...


def build_prompt(question: str, passages: list[str]) -> str:
    context = "\n".join(f"- {p}" for p in passages)
    return f"Answer using only this context:\n{context}\n\nQ: {question}"


class AnswerService:
    def __init__(self, retriever: Retriever, model: ChatModel,
                 usage: UsageRecorder, model_name: str) -> None:
        self._retriever = retriever
        self._model = model
        self._usage = usage
        self._model_name = model_name

    def answer(self, question: str) -> str:
        passages = self._retriever.search(question)
        completion = self._model.complete(build_prompt(question, passages))
        self._usage.record(self._model_name, completion)
        return completion.text
```

The classic SRP failure modes are the "does everything" method (connect, build query, run, map, close in one body) and the junk-drawer `utils.py` with 40 unrelated functions. The opposite failure is real too: splitting a 30-line function into five single-method classes buys indirection, not clarity. Split along lines of change, not along lines of nouns.

### OCP: extend by adding code, not by reopening it

Open/Closed says you should be able to add behaviour without editing code that already works and is already tested. The smell is an `if/elif` chain on a type string: every new provider, channel or discount reopens the same method, and every reopening risks the branches you did not mean to touch.

```python
from collections.abc import Sequence
from typing import Protocol


class Channel(Protocol):
    def send(self, recipient: str, message: str) -> None: ...


class EmailChannel:
    def send(self, recipient: str, message: str) -> None:
        print(f"email -> {recipient}: {message}")


class SlackChannel:
    def send(self, recipient: str, message: str) -> None:
        print(f"slack -> {recipient}: {message}")


class NotificationService:
    def __init__(self, channels: Sequence[Channel]) -> None:
        self._channels = tuple(channels)

    def notify(self, recipient: str, message: str) -> None:
        for channel in self._channels:
            channel.send(recipient, message)


class WhatsAppChannel:  # added by another team; NotificationService is untouched
    def send(self, recipient: str, message: str) -> None:
        print(f"whatsapp -> {recipient}: {message}")


NotificationService([EmailChannel(), SlackChannel(), WhatsAppChannel()]).notify("ops", "Order shipped")
```

```text
email -> ops: Order shipped
slack -> ops: Order shipped
whatsapp -> ops: Order shipped
```

Be honest about the limit: the decision of *which* channels to build still lives somewhere. OCP does not delete that decision, it moves it to a single composition point (a factory, a registry or your app startup) so that the business logic stays closed. Total closure is a myth; aim for closure against the changes you can predict, such as new providers, and accept edits for the ones you cannot.

### LSP: a signature match is not a behaviour match

Liskov Substitution says a subtype must be usable wherever its base is expected without the caller noticing. The rule is about contracts: a subtype may not strengthen preconditions, may not weaken postconditions, and may not raise exceptions the base contract does not allow. Type checkers verify the shape (parameter names, types, return type, and with `typing.override` on 3.12 they also verify that you really override something). They cannot verify the behaviour.

```python
class GoodModel:
    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        return Completion(prompt[:max_tokens])


class CappedModel:
    """Signature matches, behaviour does not: it strengthens the precondition."""
    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        if max_tokens > 256:
            raise ValueError("max_tokens must be <= 256")
        return Completion(prompt[:max_tokens])


def summarize(model: ChatModel, text: str) -> str:
    return model.complete(text).text          # relies on the default of 512
```

`summarize(GoodModel(), "hello")` works; `summarize(CappedModel(), "hello")` raises `ValueError: max_tokens must be <= 256`, from a caller that did nothing wrong. The fix is to put the real constraint in the contract (a `max_output_tokens` attribute on the Protocol that callers must respect) or to clamp inside the subclass, never to surprise the caller.

The textbook version is `Square(Rectangle)`. If `Square` overrides only `set_width` to also set the height, then `set_width(5)` followed by `set_height(10)` yields area `50`. Override both setters so that each sets both sides and the same calls yield `100`. A caller that reasons "area equals width times height" gets a different answer depending on the subtype, which is the violation. A practical detector is any `isinstance` check or `try/except` placed before a call purely to cope with one subclass, and a method body that only raises `NotImplementedError("X can't do this")`.

### ISP: let consumers declare only what they use

Interface Segregation says no client should depend on methods it does not call. A fat `LLMProvider` ABC with `chat`, `embed`, `transcribe` and `moderate` forces a chat-only vendor to implement three methods that raise, and every test fake must stub all four. With Protocols the consumer defines the narrow interface it needs, and any class with matching methods satisfies it without inheriting anything.

```python
from typing import Protocol, runtime_checkable


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class Indexer:
    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder

    def index(self, docs: list[str]) -> int:
        return len(self._embedder.embed(docs))


@runtime_checkable
class RTEmbedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
```

A class that offers both `complete` and `embed` satisfies `ChatModel` and `Embedder` simultaneously, which is the point: segregation happens at the consumer, not the implementer. Be aware that `isinstance(x, RTEmbedder)` only checks that an attribute named `embed` exists, not its signature, so use `@runtime_checkable` for dispatch, not for correctness. The multiplication problem is real as well: four independent behaviours modelled as "can/cannot" subclasses would need 2^4 = 16 classes, which is why capabilities are expressed as small separate interfaces and composition.

### DIP and DI: who you depend on versus how it arrives

Dependency Inversion says high-level policy (checkout, answer generation) and low-level detail (Razorpay SDK, an OpenAI client) should both depend on an abstraction that the high-level module owns. Dependency Injection is the mechanism that hands the concrete object in from outside. They are different things: `self.gateway = RazorpayGateway()` inside `OrderService.__init__` violates DIP twice, once by naming the concrete class and once by constructing it. Passing the gateway to the constructor fixes the second problem; typing the parameter as a `PaymentGateway` Protocol fixes the first.

The payoff is a seam. The concrete wiring happens in one composition root, and tests substitute fakes:

```python
def build_service(env: str) -> AnswerService:
    model = AnthropicChat() if env == "prod" else FakeModel()   # the only place that knows
    return AnswerService(PgVectorRetriever(), model, PostgresUsage(), model_name="prod-model")
```

In FastAPI the composition root is `Depends`, and tests swap implementations with `app.dependency_overrides[get_service] = lambda: fake_service`. SQLAlchemy's `create_engine(url)` is a familiar real-world instance: application code holds an `Engine` and never names a driver, because the URL prefix decides the dialect.

### When SOLID is overkill in Python

A Protocol with one implementation and no I/O boundary is ceremony. Python gives you cheaper tools: a `Callable[[str], Completion]` parameter is a perfectly good one-method interface, a `dict[str, Callable]` is a perfectly good open-closed dispatch table, and a module-level function is a perfectly good single-responsibility unit. Introduce a seam where something is slow, costly, non-deterministic or owned by another team, which means network calls, model providers, clocks and databases. For pure in-process logic, keep it concrete until a second implementation actually appears.

## Practical Backend Scenario

Your checkout service charges through Razorpay, and your support assistant answers from one LLM vendor. Product announces two changes: Stripe for EU customers next quarter, and a fallback model because the primary vendor had a four-hour incident last month. If `OrderService` builds `RazorpayGateway()` itself and the assistant imports a vendor SDK in six files, this is a multi-week refactor with regression risk across payments. If both services depend on `PaymentGateway` and `ChatModel` Protocols injected at the composition root, the work is two new adapter classes, a routing function that picks the gateway by country, and a tiny `FallbackChat` that wraps two `ChatModel` objects. Nobody opens `checkout()` or `answer()`. That outcome, not the acronym, is what you are demonstrating in the interview.

## Practice Loop

1. Take the `AnswerService` code above, add a `FakeModel` and a `ListRecorder`, and write a test that asserts the recorded token count without any network or database.
2. Add a second `ChatModel` implementation that wraps two models and falls back on `TimeoutError`. Confirm `AnswerService` needs zero edits.
3. Write a `CappedModel` that raises on large `max_tokens`, then write a contract test that every `ChatModel` implementation must pass (default arguments, returns a `Completion`, no unexpected exceptions). Observe which implementation fails.
4. Convert a fat `LLMProvider` ABC into `ChatModel` and `Embedder` Protocols and change a consumer to ask only for what it uses.
5. Replace one single-method Protocol with a `Callable` type alias and decide, in a sentence, which version is clearer for your team.

## Evidence of Understanding

- You can state SRP as "one reason to change, one stakeholder" and point to the actors in a given class.
- You can explain why an `if/elif` on a type string violates OCP and where the remaining decision should live instead.
- You can show a subclass with a matching signature that still violates LSP, and name the contract rule it breaks.
- You can explain why ISP is satisfied at the consumer side with Protocols, and what `@runtime_checkable` does and does not check.
- You can distinguish DIP from DI in one sentence each and identify the composition root in a codebase.
- You can name a case where applying a SOLID principle would make a Python design worse.

## Interview Questions to Rehearse

### Q: What is the difference between DIP and dependency injection?
DIP is a design rule about the direction of source-code dependencies: policy code depends on an abstraction it owns, and details depend on that same abstraction. Dependency injection is a technique for supplying a dependency from outside instead of constructing it internally. You can inject a concrete class and still violate DIP, and you can follow DIP while constructing a default object through a factory. In practice you want both: an abstraction type on the constructor parameter, and the real object chosen at one composition root.

### Q: How do you recognise an LSP violation in Python, where there are no interface keywords?
Look for behaviour the base contract does not promise: a subclass that raises where the base did not, narrows accepted values, returns a different shape, or has a method that only raises `NotImplementedError`. The practical smell is an `isinstance` check or `try/except` in calling code that exists to work around one subtype. Type checkers catch signature drift but not behaviour, so I back contracts with a shared test suite that every implementation must pass.

### Q: Does `typing.Protocol` replace ABCs?
No. Protocols give structural typing, so a third-party class conforms without inheriting, which is ideal for consumer-side interfaces and for ISP. ABCs give nominal typing plus runtime enforcement that abstract methods are implemented and a place to share template-method code. I use Protocols at module boundaries and for fakes, and an ABC when I want shared behaviour or an explicit registration point.

### Q: Show me a place where applying OCP is a mistake.
Anything with a single implementation and no realistic second one. Wrapping a pure pricing function in a strategy hierarchy adds three files and no flexibility. I apply OCP where change is predictable and costly, such as providers and channels, and I keep a plain function or `dict` dispatch for the rest, then refactor when the second case actually arrives.

### Q: Your team's `utils.py` has grown to 40 functions. Is that an SRP problem, and what do you do?
Yes, it is the junk-drawer trap: unrelated reasons to change share a file, so imports become tangled and ownership is unclear. I group functions by the actor that changes them (dates, text, storage), move them next to the code that uses them where possible, and leave a thin shim only if many importers need migration time. I do not create classes just to hold the functions.

## Common Pitfalls

- Splitting by noun instead of by reason to change, producing five tiny classes that always change together.
- Adding a Protocol for a single implementation with no I/O boundary, which only adds indirection.
- Treating a matching signature as LSP-compliant while a subclass narrows its accepted inputs or raises new exceptions.
- Relying on `isinstance(x, SomeProtocol)` with `@runtime_checkable` as a safety check; it only tests for attribute presence.
- Constructing a default concrete dependency inside `__init__` "just for convenience", which defeats DI and makes tests slow or flaky.
- Putting the `if/elif` provider switch in five places instead of one composition root.
- Using inheritance for capabilities (fly, swim, sing) and ending up with a class explosion instead of small Protocols.

## Suggested Extension

Build a `PaymentGateway` Protocol with Razorpay and Stripe adapters, a `CountryRouter` that selects one by country code, and a contract test suite that both adapters must pass. Then add a third adapter in a separate package and register it without editing the router, using a registry or an entry point, and write down what you still had to touch.
