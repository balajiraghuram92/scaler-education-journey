# Design Patterns: Factory for Service Abstraction

Almost every AI backend ends up calling more than one vendor: two LLM providers for fallback, a cloud embedding model and a local one, Razorpay and Stripe, email and SMS. The factory family is how you keep the vendor choice in one place so the rest of the code never imports an SDK class by name. Interviewers use it to test whether you can separate "who decides" from "who uses", whether you know the three variants apart, and whether you can say when none of them is warranted.

## Concepts Covered

### The problem: the vendor leak

Without a factory, the decision about which concrete class to instantiate leaks into every caller. A `ChatService` that does `if provider == "openai": client = OpenAIClient()` is coupled to every vendor it supports, and the same `if/elif` tends to be copy-pasted into the batch job, the CLI and the tests. Adding a provider means editing every copy, which is the Open/Closed violation from the SOLID lesson. A factory moves construction into one function or class, so callers depend only on an abstraction (a Protocol or ABC) and receive an object that satisfies it.

A factory centralises the decision; it does not delete it. Somewhere there is still one place that knows the full list of providers, and that place changes when a provider is added. That is the honest, defensible claim: you reduce the blast radius from "every caller" to "one module".

### Simple factory: one function, one place

The simple factory is not a Gang of Four pattern but it is the most common form: a function or static method that takes a key and returns the right product. In Python a dictionary from name to class (or any callable) is usually cleaner than an `if/elif` or `match` chain:

```python
from typing import Protocol


class ChatClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class OpenAIClient:
    def complete(self, prompt: str) -> str:
        return f"[openai] {prompt}"


class AnthropicClient:
    def complete(self, prompt: str) -> str:
        return f"[anthropic] {prompt}"


_CLIENTS: dict[str, type[ChatClient]] = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
}


def create_chat_client(provider: str) -> ChatClient:
    try:
        factory = _CLIENTS[provider.lower()]
    except KeyError:
        raise ValueError(f"unknown provider {provider!r}; expected one of {sorted(_CLIENTS)}") from None
    return factory()


class ChatService:
    def __init__(self, client: ChatClient) -> None:
        self._client = client

    def reply(self, prompt: str) -> str:
        return self._client.complete(prompt)


print(ChatService(create_chat_client("Anthropic")).reply("hi"))
```

```text
[anthropic] hi
```

Note that `ChatService` receives a client and never calls the factory itself; the factory runs at the composition root. If `ChatService` calls `AIServiceClientProvider.get_client(provider)` in its own constructor it is better than hard-coding, but it still cannot be tested with a fake without patching, so prefer injecting the result.

Four bugs show up repeatedly in simple factories. Passing `*args` on as a single tuple (`EmailNotification(args)`) instead of unpacking it (`EmailNotification(*args)`) fails with `missing 1 required positional argument`. Forgetting `@staticmethod` makes `factory.create("mp3", 50)` fail with `takes 2 positional arguments but 3 were given`, because `self` is passed automatically. Building a dict of *instances* (`{"a": A(), "b": B(), "c": C()}.get(kind)`) constructs every product on every call, so store classes or callables and call only the chosen one. And `{...}.get(kind)(...)` for an unknown key raises the unhelpful `'NoneType' object is not callable`; raise a `ValueError` that lists the valid keys.

### Factory method: let a subclass decide

The factory method pattern puts the creation step in an overridable method of a base class, and the base class's other logic calls it.

```python
class ChatWorkflow:
    def create_client(self) -> ChatClient:
        raise NotImplementedError

    def reply(self, prompt: str) -> str:
        return self.create_client().complete(prompt)


class AnthropicWorkflow(ChatWorkflow):
    def create_client(self) -> ChatClient:
        return AnthropicClient()
```

It suits frameworks where a template method owns the algorithm and subclasses supply one variable piece. In Python it is often replaced by passing a callable (`ChatWorkflow(client_factory=AnthropicClient)`), which avoids a subclass per provider. Reach for the subclass form when the creation step is one of several overridden steps, not when it is the only variation.

### Abstract factory: a family that must match

Use the abstract factory when you create several related objects that must be compatible with each other. In an AI system the classic family is the chat model, the embedder and the vector index from one provider, because the index must be created with the dimensionality of the embedder that fills it. Mixing a 384-dimension local embedder with a 1536-dimension index breaks at insert time. The abstract factory makes the wrong combination impossible to construct:

```python
from abc import ABC, abstractmethod


class AIKit(ABC):  # ChatModel, Embedder, VectorIndex are Protocols; the concrete products are small fakes
    @abstractmethod
    def chat(self) -> ChatModel: ...

    @abstractmethod
    def embedder(self) -> Embedder: ...

    def index(self) -> VectorIndex:
        return FixedDimIndex(self.embedder().dimensions)


class OpenAIKit(AIKit):
    def chat(self): return OpenAIChat()
    def embedder(self): return OpenAIEmbedder()     # 1536 dimensions


class LocalKit(AIKit):
    def chat(self): return LocalChat()
    def embedder(self): return LocalEmbedder()      # 384 dimensions


def ingest(kit: AIKit, docs: list[str]) -> tuple[int, int]:
    embedder, index = kit.embedder(), kit.index()
    for doc in docs:
        index.add(embedder.embed(doc))
    return len(index.rows), embedder.dimensions
```

`ingest(OpenAIKit(), ["a", "b"])` returns `(2, 1536)` and `ingest(LocalKit(), ["a"])` returns `(1, 384)`; hand-pairing a 1536-dimension index with the local embedder raises `ValueError: expected 1536 dims, got 384`. The abstract base class also gives you a guard: `AIKit()` raises `TypeError: Can't instantiate abstract class AIKit without an implementation for abstract methods 'chat', 'embedder'`. A method such as `supports_format()` on each concrete factory lets a dispatcher ask which factory handles a given input.

The cost is one factory class per family and a new method on every factory whenever a new product kind appears. So the lecture's guidance holds: use an abstract factory only when a genuine family must stay matched; for a single product, a simple factory is enough.

### Config-driven and plugin factories

In production the key comes from configuration, and third-party providers should plug in without editing your code. Combine the factory with the registry from the previous lesson: providers register themselves (decorator, `__init_subclass__`) and installed packages declare an entry point that the factory loads lazily.

```python
from importlib.metadata import entry_points

_REGISTRY: dict[str, type] = {}


def provider(name: str):
    def decorator(cls):
        _REGISTRY[name] = cls
        return cls
    return decorator


def load_plugins(group: str = "myapp.chat_providers") -> None:
    for ep in entry_points(group=group):
        _REGISTRY.setdefault(ep.name, ep.load())    # built-ins win over plugins
```

`functools.partial` is a handy factory for pre-configured creation: `partial(OpenAIClient, model="small", timeout=10)` is a zero-argument factory with settings baked in, and it can be stored in the same registry.

### When a factory is overkill

With one provider and no realistic second, a direct constructor call is clearer. A factory earns its place when there are several implementations, the choice depends on configuration or runtime data, or tests need a seam. It is also unnecessary when a plain function parameter already does the job: passing `client: ChatClient` into the constructor is dependency injection, and the factory is just the code at the top that builds it.

## Practical Backend Scenario

A support product launches with one LLM vendor. Six months later the vendor has an outage, finance wants a cheaper model for low-risk intents, and a regulated customer demands an on-prem model. The team had a `create_chat_client(settings)` factory and a `ChatClient` Protocol from day one, so the work is two adapter classes, two registry entries and a routing function in the composition root. The embedding pipeline needed more care: switching to the local model changed the vector dimension, which would have corrupted the index. Because they created embedder and index through an `AIKit`, the new kit built a 384-dimension index automatically and the pipeline rebuilt it instead of silently mixing dimensions. Interviewers value exactly this narrative: the factory choice is driven by a real failure mode, not by pattern enthusiasm.

## Practice Loop

1. Write the `ChatClient` Protocol, three fake clients and a dict-based `create_chat_client` that raises a helpful `ValueError`. Add a test for the unknown-provider message.
2. Reproduce the three bugs: `args` passed as one tuple, a missing `@staticmethod`, and a dict of instances. Record each error message.
3. Build `AIKit`, `OpenAIKit` and `LocalKit`, then show the dimension mismatch error when you pair them by hand and its absence when you use the kit.
4. Replace the factory method subclass with a callable parameter and compare the amount of code.
5. Add a `provider` decorator and a `load_plugins` function; verify that a name registered by a built-in is not overridden by a plugin.

## Evidence of Understanding

- You can state what a simple factory, a factory method and an abstract factory each provide, and name the problem that selects each.
- You can explain what a factory centralises and why it does not remove the decision.
- You can diagnose the three classic simple-factory bugs from their error messages.
- You can give an example of a product family that must stay matched.
- You can describe how entry points let third parties add providers without editing your code.
- You can argue when a direct constructor is better than a factory.

## Interview Questions to Rehearse

### Q: What problem does a Simple Factory solve?
It removes repeated `if/elif` creation logic from callers by putting the decision in one place, so adding a provider changes one module instead of many. It reduces coupling to concrete classes but does not remove the decision, which is why I describe it as partial Open/Closed compliance.

### Q: How do Factory Method and Abstract Factory differ?
Factory Method is one overridable creation step inside a class hierarchy; a subclass decides which product to make. Abstract Factory is an object that creates a whole family of related products and guarantees they match, such as an embedder and an index with the same dimensions. Abstract Factory is often built from several factory methods.

### Q: When would you not use a factory in Python?
When there is one implementation and no test seam, or when passing a callable or an already built object into the constructor is enough. Python's first-class functions make many factories unnecessary: `functools.partial` or a dict of callables covers most cases.

### Q: How would you let customers add their own provider without changing your code?
Define a Protocol for the provider, a registry keyed by name, and an entry-point group such as `myapp.chat_providers`. Customer packages declare an entry point, and my factory loads them with `importlib.metadata.entry_points(group=...)` at start-up, rejecting duplicate names. Contract tests ensure that each provider honours the Protocol.

### Q: Why is `ChatService` calling `get_client(provider)` internally not ideal?
It is better than hard-coding a vendor class, but the service still depends on the factory and the provider name, so tests need patching and the service cannot receive a custom client. I prefer building the client at the composition root and injecting it.

## Common Pitfalls

- Passing `*args` through as one tuple instead of unpacking it.
- Defining a factory method without `@staticmethod` or `@classmethod` and then hitting a `TypeError` about argument counts.
- Building every product eagerly in a dict literal instead of storing classes or callables.
- Returning `None` for unknown keys, which fails far from the cause.
- Reaching for an abstract factory when only one object is created.
- Letting service classes call the factory themselves, which keeps the vendor knowledge in the wrong layer.
- Registering plugins by import side effects and then forgetting to import them in production.

## Suggested Extension

Extend `AIKit` with a `create_reranker()` product and a third kit. Load kits from an entry-point group, select one from settings with a fallback kit if the preferred provider's package is missing, and write a contract test that runs every registered kit through the same ingest-and-query scenario with fake network calls.
