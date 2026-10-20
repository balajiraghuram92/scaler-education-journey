# Design Patterns: Adapter and Facade

Almost every AI or backend system you will touch at work sits on top of code you do not own: three LLM vendors, a payment gateway, a vector database. Adapter and Facade are the two structural patterns that keep that foreign code from leaking into your domain. Interviewers love them because they look identical on a whiteboard (a class that wraps another class) and the candidate who can say precisely which problem each solves, and how they compose, immediately reads as senior.

## Concepts Covered

### Structural patterns in one paragraph

Creational patterns (Singleton, Builder, Factory) decide how objects come into existence. Structural patterns decide how existing objects are composed into larger structures. Adapter, Facade, Decorator, Proxy and Flyweight are all structural. A Builder assembles an object; an Adapter connects an object that already exists to a client that cannot call it as-is. That is the whole classification argument.

### Adapter: one interface over several LLM SDKs

The Adapter translates an interface you cannot change (the **adaptee**) into the interface your code expects (the **target**). Three roles: the client depends on the target, the adaptee is foreign, and the adapter implements the target by delegating to the adaptee. The translation covers more than method names. It covers parameter shapes, units, response structure, status codes and, critically, **errors**.

In Python the target is usually a `typing.Protocol` or an ABC, and the adapter uses composition (an object adapter). The class-adapter variant, inheriting from the adaptee as well as the target, works through multiple inheritance but welds you to the vendor class and its MRO, so it is rarely the right call.

The two vendor classes below are stand-ins with deliberately different shapes. Real SDKs differ in the same ways: message lists versus plain prompts, nested dicts versus attribute access, different names for token limits.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ChatRequest:
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.0


@dataclass(frozen=True, slots=True)
class ChatReply:
    text: str
    input_tokens: int
    output_tokens: int


class ModelUnavailable(Exception):
    """Provider-neutral error the rest of the app catches."""


class ChatModel(Protocol):          # the target interface
    def generate(self, request: ChatRequest) -> ChatReply: ...


# Stand-ins for vendor SDKs we do not own
class AcmeChatClient:
    def create_completion(self, *, messages: list[dict], max_tokens: int, temperature: float) -> dict:
        user = messages[-1]["content"]
        return {"choices": [{"message": {"content": f"acme:{user}"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 7}}


class NimbusClient:
    def generate(self, text: str, max_output_tokens: int, creativity: float):
        class Result:
            output = f"nimbus:{text}"
            tokens_in, tokens_out = 10, 5
        return Result()


class AcmeAdapter:
    def __init__(self, client: AcmeChatClient) -> None:
        self._client = client

    def generate(self, request: ChatRequest) -> ChatReply:
        try:
            raw = self._client.create_completion(
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except ConnectionError as exc:
            raise ModelUnavailable("acme unreachable") from exc
        return ChatReply(raw["choices"][0]["message"]["content"],
                         raw["usage"]["prompt_tokens"],
                         raw["usage"]["completion_tokens"])


class NimbusAdapter:
    def __init__(self, client: NimbusClient) -> None:
        self._client = client

    def generate(self, request: ChatRequest) -> ChatReply:
        r = self._client.generate(request.prompt, request.max_tokens, request.temperature)
        return ChatReply(r.output, r.tokens_in, r.tokens_out)


def summarise(model: ChatModel, text: str) -> str:
    return model.generate(ChatRequest(f"Summarise: {text}")).text


for m in (AcmeAdapter(AcmeChatClient()), NimbusAdapter(NimbusClient())):
    print(summarise(m, "q3 report"))
```

```text
acme:Summarise: q3 report
nimbus:Summarise: q3 report
```

`summarise` never imports a vendor module. Adding a third provider is a new adapter class and one line of wiring, which is the Open/Closed Principle paying rent.

### Adapter with a bank gateway: the translation is the point

The Scaler example is PhonePe talking to banks. Look at what the adapter must translate: the argument order differs, and the vendor signals success with `0` rather than a boolean.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Bank:
    account_number: str
    account_holder_name: str


class BankAPI(ABC):
    @abstractmethod
    def add_bank_account(self, bank: Bank) -> None: ...
    @abstractmethod
    def pay(self, amount: float, account: str) -> bool: ...


class YesBank:                       # third-party: cannot be edited
    def open_account(self, acc_number, holder_name):
        print(f"YesBank opened {acc_number} for {holder_name}")
    def do_payment(self, account, amt):
        return 0                     # vendor convention: 0 means success


class YesBankAdapter(BankAPI):
    def __init__(self, yes_bank: YesBank) -> None:
        self._yes_bank = yes_bank
    def add_bank_account(self, bank: Bank) -> None:
        self._yes_bank.open_account(bank.account_number, bank.account_holder_name)
    def pay(self, amount: float, account: str) -> bool:
        return self._yes_bank.do_payment(account, amount) == 0


class PhonePe:
    def __init__(self, banks: dict[str, BankAPI]) -> None:
        self._banks = banks          # registry: no if/elif chain to edit
    def pay(self, bank_name: str, amount: float, account: str) -> bool:
        return self._banks[bank_name].pay(amount, account)


print(PhonePe({"yes": YesBankAdapter(YesBank())}).pay("yes", 100.0, "ACC1"))
```

```text
True
```

The dictionary registry matters. If `PhonePe` contains `if bank == "YesBank": ... elif ...`, you built adapters and then re-coupled the client to every one of them, so adding a bank still edits `PhonePe`.

### Facade: one entry point over an ingestion pipeline

A Facade gives a **simpler** interface to a subsystem of several collaborators. It does not translate incompatible interfaces; it coordinates. The classic AI-engineering instance is document ingestion: load, chunk, embed, store, always in that order.

```python
from dataclasses import dataclass
from typing import Protocol


class Loader(Protocol):
    def load(self, uri: str) -> str: ...
class Chunker(Protocol):
    def split(self, text: str) -> list[str]: ...
class Embedder(Protocol):
    def embed(self, chunks: list[str]) -> list[list[float]]: ...
class VectorStore(Protocol):
    def upsert(self, doc_id: str, chunks: list[str], vectors: list[list[float]]) -> None: ...


@dataclass(frozen=True)
class IngestReport:
    doc_id: str
    chunks: int


class IngestionFacade:
    def __init__(self, loader: Loader, chunker: Chunker, embedder: Embedder, store: VectorStore) -> None:
        self._loader, self._chunker, self._embedder, self._store = loader, chunker, embedder, store

    def ingest(self, uri: str) -> IngestReport:
        text = self._loader.load(uri)
        chunks = self._chunker.split(text)
        vectors = self._embedder.embed(chunks)
        self._store.upsert(uri, chunks, vectors)
        return IngestReport(doc_id=uri, chunks=len(chunks))
```

Two design rules. First, the facade is **not a wall**: the subsystems stay public, so a power user can still call the embedder directly. Second, the collaborators are injected through the constructor. A facade that builds its own `Embedder()` inside `__init__` cannot be unit tested without hitting the real service, whereas an injected one runs against in-memory fakes:

```python
class FakeLoader:
    def load(self, uri): return "a b c d e f"
class WordPairChunker:
    def split(self, text):
        w = text.split()
        return [" ".join(w[i:i + 2]) for i in range(0, len(w), 2)]
class FakeEmbedder:
    def embed(self, chunks): return [[float(len(c))] for c in chunks]
class MemoryStore:
    def __init__(self): self.rows = {}
    def upsert(self, doc_id, chunks, vectors): self.rows[doc_id] = list(zip(chunks, vectors))


store = MemoryStore()
print(IngestionFacade(FakeLoader(), WordPairChunker(), FakeEmbedder(), store).ingest("s3://docs/a.txt"))
print(store.rows["s3://docs/a.txt"][0])
```

```text
IngestReport(doc_id='s3://docs/a.txt', chunks=3)
('a b', [3.0])
```

### Adapter versus Facade, and how they combine

| | Adapter | Facade |
|---|---|---|
| Problem | Interface mismatch | Subsystem complexity |
| Wraps | Usually one object | Several objects |
| Changes the interface? | Yes, to a known target | Yes, to a simpler new one |
| Adds behaviour? | No, only translation | Adds coordination and ordering |
| Typical name | `XyzAdapter` | `XyzService`, `XyzFacade`, `Client` |

They compose naturally. A `book_ride()` facade coordinates fare calculation, driver matching and notification, and it talks to maps through a `MapProvider` interface that has one adapter per maps SDK. The facade is the front door; the adapters live behind it. A wrapper around a single third-party class that merely renames methods is an adapter, however many people call it a facade.

> **Interview tip:** Say the intent out loud: "Adapter makes an existing interface match one my client expects; Facade offers a new, simpler interface over several parts." Then say which one you would reach for given the prompt, and why. Naming the intent beats naming the UML.

> **Pitfall:** A facade that accumulates business rules becomes a god class. If it starts holding state or making domain decisions, split it: the facade orchestrates, the services decide.

## Practical Backend Scenario

You join a customer engagement as a forward deployed engineer. The prototype calls one LLM vendor directly in forty places, reading `response["choices"][0]["message"]["content"]`. The customer's security team now mandates a different, self-hosted model, and finance wants token usage per request regardless of provider. If the vendor SDK is spread through the code, you are rewriting forty call sites. If you introduce a `ChatModel` target and one adapter per provider that returns a normalised `ChatReply` (text plus token counts) and raises `ModelUnavailable`, the migration is one new adapter, and usage metering sits in one place. On top, an `AnswerService` facade (retrieve, prompt, generate, post-process) gives the web layer a single `answer(question)` call. The outcome of the engagement hinges on those seams, not on prompt cleverness.

## Practice Loop

1. Type out the `ChatModel` Protocol, `ChatRequest`, `ChatReply` and both adapters. Run the loop and confirm the output matches.
2. Add a third stand-in vendor whose client raises `TimeoutError` and returns the reply as a plain string. Write its adapter and map the error to `ModelUnavailable`. Notice that `summarise` does not change.
3. Write `FakeChatModel` that returns canned replies. Test `summarise` with it and without any vendor class on the import path.
4. Implement `IngestionFacade` and run it against the fakes. Then add a second `ingest_many(uris)` method and decide what should happen when the third of five documents fails.
5. Remove the constructor injection from the facade (build the collaborators inside `__init__`) and try to test it. Write down exactly what you can no longer do.
6. Replace the dictionary in `PhonePe` with an `if/elif` chain, add one more bank, and count how many classes you had to edit in each version.

## Evidence of Understanding

- I can state in one sentence why a wrapper around a single vendor class is an Adapter and not a Facade.
- I can list at least four things an adapter must translate: names, argument order, units or status codes, response shape, and exceptions.
- I can show, with a registry dictionary, how a client stays closed to modification when a new adapter is added.
- I can explain why constructor injection makes a facade testable without mocks.
- I can describe where adapters and a facade coexist in one design, and draw it.

## Interview Questions to Rehearse

### Q: What is the difference between Adapter and Facade?

Adapter fixes an interface mismatch: it makes an existing class usable through the interface a client already expects, and it normally wraps one object. Facade reduces complexity: it presents a new, simpler interface over a group of collaborators and coordinates them. Both wrap, but the motivation differs. One is about compatibility, the other about simplification.

### Q: You must support OpenAI-style, Anthropic-style and Gemini-style SDKs. How do you structure that?

I define my own `ChatModel` Protocol with provider-neutral request and reply types, then write one adapter per SDK that translates request shape, response shape, token accounting and exceptions into those types. The application only imports the Protocol. Provider choice is wiring (a registry or config), not branching in business code. Retries, caching and metrics are layered on afterwards with decorators, not inside the adapters.

### Q: Why is an if/elif on the bank name inside the client a smell even when adapters exist?

Because the client again knows every concrete adapter, so adding a provider means editing the client, violating Open/Closed. Inject the adapter, or look it up in a registry keyed by name, so the client depends only on the abstraction.

### Q: Where do exceptions belong in an adapter?

At the boundary. Vendor-specific exceptions and error codes should be translated into your own exception hierarchy inside the adapter, chaining the original with `raise ... from exc`. Otherwise `except vendor.RateLimitError` leaks into the domain and you have not actually isolated the vendor.

### Q: How would you test a facade that coordinates four services?

Inject the collaborators through the constructor and pass in-memory fakes that record calls. Assert on the observable outcome (what the store contains, what the report says) and on ordering where the order is part of the contract. A facade that constructs its own dependencies forces patching and is a design smell.

## Common Pitfalls

- Calling a single-class wrapper a Facade. If no multi-subsystem coordination exists, it is an adapter.
- Translating only method names and forgetting units, argument order, status conventions and exceptions.
- Letting vendor types (response dicts, SDK enums) escape the adapter into domain code.
- Building collaborators inside the facade, which kills testability and swapping.
- Turning the facade into a god class that owns state and business rules.
- Hiding the subsystems entirely, so advanced callers have no escape hatch.
- Adapters that compare against the wrong type, for example checking `status == "APPROVED"` when the vendor returns an Enum. Unit tests that mock the vendor with a string will never catch it; add one integration-style test against the real vendor type.

## Suggested Extension

Build a `ModelRouter` that implements `ChatModel` itself, holds an ordered list of adapters, and falls back to the next one when it catches `ModelUnavailable`. Notice that the router is both a client of the target interface and an implementation of it, which is exactly the shape the Decorator pattern generalises in the next lesson.
