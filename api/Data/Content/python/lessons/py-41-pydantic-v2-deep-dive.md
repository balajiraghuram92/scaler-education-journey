# Pydantic v2 in Depth

Every FastAPI request, every LLM tool-call argument, every config file and every webhook payload in a modern Python AI backend passes through Pydantic, which makes it the layer where bad data is either stopped or leaked. Interviewers go beyond "it validates types": they ask what runs before and after parsing, when coercion bites you, how to model a tagged union, why a hot path got slow, and which v1 habits silently break on v2. The code targets Pydantic 2.x (with `pydantic-settings` 2.x) on Python 3.12.

## Concepts Covered

### BaseModel and Field constraints

A model is a class whose annotated attributes are parsed and validated at construction by `pydantic-core`, a Rust validator. `Field` attaches constraints and metadata: numeric bounds (`gt`, `ge`, `lt`, `le`), `min_length`/`max_length` for strings and collections, `pattern` for regular expressions, `default_factory` for mutable defaults, and `max_digits`/`decimal_places` for `Decimal`. Model-wide behaviour lives in `model_config = ConfigDict(...)`.

```python
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class CompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    llm: str = Field(pattern=r"^[a-z0-9][a-z0-9.\-]*$")
    messages: list[ChatMessage] = Field(min_length=1)
    max_tokens: int = Field(default=1024, gt=0, le=32_000)
    temperature: float = Field(default=0.7, ge=0, le=2)
    user_id: str = Field(alias="userId")

    @field_validator("messages")
    @classmethod
    def last_message_is_from_user(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        if v[-1].role != "user":
            raise ValueError("the last message must come from the user")
        return v

    @model_validator(mode="after")
    def prompt_fits_context(self) -> Self:
        if self.approx_prompt_tokens + self.max_tokens > 128_000:
            raise ValueError("prompt plus max_tokens exceeds the 128k context window")
        return self

    @computed_field
    @property
    def approx_prompt_tokens(self) -> int:
        return sum(len(m.content) for m in self.messages) // 4
```

Construction goes through `CompletionRequest(...)`, `CompletionRequest.model_validate(dict)` or `CompletionRequest.model_validate_json(raw)`; any failure raises `ValidationError`, whose `.errors()` is a list of dictionaries with `loc`, `msg` and `type`. `extra="forbid"` turns a typo such as `max_tokenz` into an error; the default (`ignore`) silently drops unknown keys and the request quietly runs with the default `max_tokens`. Because of the alias, the incoming JSON key is `userId`; `populate_by_name=True` also allows the Python name `user_id` in code.

### field_validator and model_validator modes

A validator has a *mode* that fixes where it runs relative to Pydantic's own parsing.

| Mode | Receives | Typical use |
|---|---|---|
| `before` | the raw input, any type | normalise: split `"a,b"` into a list, unwrap a vendor envelope |
| `after` (default) | the parsed, typed value | business rules on a valid value |
| `wrap` | the raw input plus a `handler` that runs the inner validation | try/catch around parsing, fallbacks, logging |
| `plain` | the raw input; replaces Pydantic's own validation | fully custom parsing |

Field validators are written as `@field_validator("name")` stacked on a `@classmethod`. Model validators in `after` mode are instance methods that must return `self`; in `before` mode they are classmethods receiving the raw data, which is where you reshape input dictionaries. Raise `ValueError` or `AssertionError` (or `PydanticCustomError`) to produce a validation error; any other exception type, such as `TypeError` or `KeyError`, escapes as a crash and becomes a 500 in a web service. Validators do not run on defaults unless `validate_default=True`.

```python
from pydantic import BaseModel, field_validator


class SearchParams(BaseModel):
    tags: list[str] = []

    @field_validator("tags", mode="before")
    @classmethod
    def split_csv(cls, v: object) -> object:
        if isinstance(v, str):                       # "a, b" arrives from a query string
            return [part.strip() for part in v.split(",") if part.strip()]
        return v                                     # let normal validation handle the rest
```

### Serialization: model_dump and model_dump_json

`model_dump()` returns Python objects (a `Decimal` stays a `Decimal`, a `datetime` stays a `datetime`). `model_dump(mode="json")` returns only JSON-safe types, and `model_dump_json()` returns the JSON string directly and is faster than dumping to a dict and calling `json.dumps`. The options you are expected to know: `by_alias`, `exclude_none`, `exclude_unset` (fields not provided by the caller, the PATCH idiom), `exclude_defaults`, and `include`/`exclude` sets.

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_serializer


class Receipt(BaseModel):
    id: UUID
    total: Decimal
    issued_at: datetime
    note: str | None = None

    @field_serializer("total")
    def total_as_string(self, v: Decimal) -> str:
        return f"{v:.2f}"


def to_wire(r: Receipt) -> str:
    return r.model_dump_json(exclude_none=True)       # UUID, Decimal, datetime handled for you
```

Passing the output of `model_dump()` to `json.dumps` fails on `UUID`, `Decimal` and `datetime`; use `mode="json"` or `model_dump_json()`. `computed_field` properties appear in `model_dump` and the JSON schema, while a plain `@property` does not.

### Aliases

`Field(alias="userId")` sets one name for both validation and serialization. For asymmetric APIs use `validation_alias` (accepted on input) and `serialization_alias` (emitted when `by_alias=True`). A generator such as `ConfigDict(alias_generator=to_camel)` with `from pydantic.alias_generators import to_camel` converts every field name at once. Serialization uses field names unless you pass `by_alias=True`; FastAPI response models do this by default.

### Strict versus lax mode

By default Pydantic runs in **lax** mode and coerces sensible inputs: `"42"` becomes `42` for an `int` field and `3.0` is accepted, while `3.5` is rejected. **Strict** mode refuses coercion. Enable it per field (`Field(strict=True)` or `StrictInt`), per model (`ConfigDict(strict=True)`) or per call (`model_validate(data, strict=True)`). For untrusted JSON money fields and IDs, strictness avoids surprises such as a boolean or string silently accepted as a number. JSON input and Python input have slightly different rules in strict mode, for example JSON strings can be parsed as dates, so test the path you actually use.

### Discriminated unions

When a payload can be one of several shapes, mark a literal field as the discriminator. Pydantic reads the tag first and validates only the matching variant, which gives precise errors and faster validation than trying each member in turn.

```python
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Card(BaseModel):
    kind: Literal["card"]
    last4: str = Field(pattern=r"^\d{4}$")


class Upi(BaseModel):
    kind: Literal["upi"]
    vpa: str


class BankTransfer(BaseModel):
    kind: Literal["bank"]
    iban: str


PaymentMethod = Annotated[Card | Upi | BankTransfer, Field(discriminator="kind")]


class Charge(BaseModel):
    amount_cents: int = Field(gt=0)
    method: PaymentMethod
```

A payload with `kind: "paypal"` fails with a single "invalid tag" error rather than one error per variant. Without a discriminator Pydantic uses *smart mode*: it tries all members and picks the best match, so errors list every branch and ambiguous inputs can match the wrong class.

### TypeAdapter

`TypeAdapter` gives validation and serialization for any type, with no `BaseModel` required: a list of models, a `dict[str, int]`, a discriminated union, a `TypedDict`. Build it once at module level; constructing the validator is the expensive step.

```python
from pydantic import TypeAdapter, ValidationError

CHARGES = TypeAdapter(list[Charge])


def parse_charges(raw: bytes) -> list[Charge]:
    try:
        return CHARGES.validate_json(raw)        # parses and validates in one Rust pass
    except ValidationError as exc:
        raise ValueError(exc.errors(include_url=False)) from exc
```

`validate_json` parses and validates in a single step, which beats `json.loads` followed by `validate_python`. Other useful methods are `validate_python`, `dump_python`, `dump_json` and `json_schema()`.

### pydantic-settings

Configuration is validated input too. In v2 `BaseSettings` lives in the separate `pydantic-settings` package. It reads environment variables (case-insensitively), an optional `.env` file, and secrets directories, and validates them on construction so a bad deployment fails at start-up instead of at 3 a.m.

```python
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GATEWAY_", env_file=".env", env_nested_delimiter="__", extra="ignore"
    )

    openai_api_key: SecretStr
    request_timeout_s: float = 30.0
    max_concurrency: int = Field(default=16, gt=0)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()        # reads GATEWAY_OPENAI_API_KEY, GATEWAY_MAX_CONCURRENCY, ...
```

`SecretStr` hides the value in `repr` and logs; call `.get_secret_value()` where it is really needed. `BaseSettings` defaults to forbidding extra keys, so a `.env` file with unrelated entries fails validation unless you set `extra="ignore"`. Cache the instance (`lru_cache` or a FastAPI dependency) rather than re-reading the environment per request.

### v1 to v2 migration traps

| v1 habit | v2 |
|---|---|
| `.dict()`, `.json()`, `parse_obj()` | `model_dump()`, `model_dump_json()`, `model_validate()` (old names still exist but warn) |
| `@validator`, `@root_validator` | `@field_validator`, `@model_validator` |
| `class Config:` with `orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| `allow_population_by_field_name` | `populate_by_name` |
| `__fields__`, `update_forward_refs()` | `model_fields`, `model_rebuild()` |
| `regex=`, `min_items=` | `pattern=`, `min_length=` |
| `from pydantic import BaseSettings` | `from pydantic_settings import BaseSettings` |

Behavioural traps are worse than renames. A field typed `str | None` with no default is now **required** (it may be `None`, but the caller must supply it); in v1 it was implicitly optional. Lax mode no longer coerces numbers into `str`. Validation of a model instance passed into another model does not re-validate it by default. And `ValidationError` messages and `type` codes changed, which breaks tests that match error text.

### Performance

The validator core is Rust, so most slowness is self-inflicted. Build `TypeAdapter`s and models at import time, not per call. Prefer `model_validate_json` over `json.loads` plus `model_validate`. Python-level validators (especially `wrap` and `plain`) call back into Python for each value, so keep them out of per-item hot paths and prefer built-in constraints. `model_construct()` skips validation entirely and is only safe for data you already trust. For large flat records, consider a `TypedDict` with a `TypeAdapter`, which avoids creating model instances when you only need validated dictionaries.

## Practical Backend Scenario

Your LLM gateway receives webhooks from three providers, each a JSON array of tagged events, and loads its configuration from the environment. One malformed event must not take down the batch, secrets must never reach the logs, and a payload with an unknown event type must be reported precisely. The design: a discriminated union of event models, a module-level `TypeAdapter` for single events, per-item validation that collects errors, and `Settings` with `SecretStr` that fails at start-up.

```python
import json
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class Succeeded(BaseModel):
    type: Literal["payment.succeeded"]
    id: str
    amount_cents: int = Field(gt=0)


class Failed(BaseModel):
    type: Literal["payment.failed"]
    id: str
    reason: str


Event = Annotated[Succeeded | Failed, Field(discriminator="type")]
EVENT = TypeAdapter(Event)                       # built once


def parse_batch(raw: bytes) -> tuple[list[Succeeded | Failed], list[dict[str, object]]]:
    good: list[Succeeded | Failed] = []
    bad: list[dict[str, object]] = []
    for index, item in enumerate(json.loads(raw)):
        try:
            good.append(EVENT.validate_python(item))
        except ValidationError as exc:
            bad.append({"index": index, "errors": exc.errors(include_url=False, include_input=False)})
    return good, bad
```

An event with `type: "payment.refunded"` is reported as an invalid tag for that index only, and `amount_cents: 0` is reported with its location, while the rest of the batch is processed. The bad entries go to a dead-letter store with their index and error list, and metrics count them per provider.

## Practice Loop

1. Build `CompletionRequest` and try: a missing `userId`, a typo field, `temperature=3`, a last message from the assistant, and a request whose `max_tokens` blows the context budget. Print `exc.errors()` for each.
2. Add `mode="before"` validators that accept `"a, b"` for a list field, and a `wrap` validator that logs and falls back to a default on failure.
3. Dump a model containing `UUID`, `Decimal` and `datetime` with `model_dump()`, `model_dump(mode="json")` and `model_dump_json()`, and see which of them `json.dumps` accepts.
4. Compare `Union[Card, Upi]` with and without `discriminator`, using a payload with a wrong tag, and read both error lists.
5. Write `Settings` with `SecretStr`, run it with and without the environment variables, and confirm the secret is masked in `repr`.
6. Take a v1-style model (`class Config`, `@validator`, `Optional[int]` without default) and migrate it. Then complete the coding assignments below.

## Evidence of Understanding

- I can say which validator mode receives raw input versus parsed values, and what a `wrap` validator is for.
- I can predict lax versus strict results for `"42"`, `3.0` and `3.5` on an `int` field.
- I can choose between `model_dump`, `model_dump(mode="json")` and `model_dump_json`, and explain `exclude_unset`.
- I can model a tagged union with a discriminator and explain the error and performance benefit.
- I can explain why a `TypeAdapter` belongs at module level and why `model_validate_json` is faster.
- I can describe how `pydantic-settings` loads and validates configuration and why extra keys can fail.
- I can list the v1 traps that change behaviour rather than names, starting with required `Optional` fields.

## Interview Questions to Rehearse

### Q: What is the difference between `mode="before"`, `after`, `wrap` and `plain` validators?
`before` receives the raw input before Pydantic parses it, so it normalises shapes. `after` receives the typed, validated value and applies business rules. `wrap` receives the raw input and a handler, so it can run the standard validation inside a try/except or transform around it. `plain` replaces the built-in validation entirely. The more Python code a mode runs per value, the more it costs in hot paths.

### Q: When does lax mode bite, and when do you use strict mode?
Lax mode coerces, so `"42"` becomes `42` and `"true"` becomes `True`, which can mask client bugs and let ambiguous input through. Use strict mode for security-sensitive or financial fields, and for IDs where a string must not silently become a number. Apply it per field, per model or per call, and test with the actual input source, JSON or Python.

### Q: Why use a discriminated union instead of a plain union?
A discriminator makes Pydantic read the tag and validate only one variant. Errors point at that variant instead of listing every branch, validation is faster, and a wrong tag gives one clear "invalid tag" error. A plain union uses smart mode, tries all members and can pick the wrong one for ambiguous data.

### Q: A v1 model has `note: Optional[str]` and no default. What changes in v2?
In v2 the annotation only says the value may be `None`; the field is required unless it has a default. Existing callers that omitted it start failing validation. The fix is to write `note: str | None = None`. It is one of the most common migration surprises.

### Q: How do you make validation fast in a high-throughput service?
Create models and `TypeAdapter`s once at import time, validate from bytes with `model_validate_json` or `validate_json`, use built-in constraints instead of Python validators, avoid wrap and plain validators in per-item loops, and use `model_construct` only for already-trusted data. Measure first, because the Rust core is already fast and the bottleneck is often elsewhere.

### Q: How would you handle configuration and secrets with Pydantic?
Use `pydantic-settings` `BaseSettings` with an env prefix, typed fields and `SecretStr` for credentials, construct it once at start-up so a bad deployment fails fast, and inject the cached instance. Keep `.env` for local development only, and set `extra="ignore"` when the file contains unrelated keys.

## Common Pitfalls

- Treating `Optional[X]` as optional in v2, when it is required without an explicit default.
- Raising `TypeError` or `KeyError` in a validator; only `ValueError`, `AssertionError` and `PydanticCustomError` become validation errors.
- Forgetting `return self` in an `after` model validator, or `@classmethod` under a `field_validator`.
- Passing `model_dump()` output to `json.dumps` and crashing on `UUID`, `Decimal` or `datetime`.
- Using floats for money; prefer `Decimal` with `max_digits` and `decimal_places`, or integer cents.
- Leaving the default `extra="ignore"` on request models, so typos in field names silently disappear.
- Constructing `TypeAdapter` or models inside request handlers.
- Matching on Pydantic error message text in tests instead of the stable `type` code.
- Reading `os.environ` directly all over the code instead of validating one `Settings` object.

## Suggested Extension

Add a per-provider webhook adapter layer. Each provider has its own payload shape, normalised into your canonical `Event` union with a `before` model validator, and a `wrap` validator that records unknown optional fields to a metrics counter instead of failing. Generate the JSON schema with `TypeAdapter(Event).json_schema()` and write a test that fails when a field is removed from the canonical schema, so that downstream consumers are protected.
