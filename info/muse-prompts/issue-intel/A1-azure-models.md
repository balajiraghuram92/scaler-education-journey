# A1 — Real models for the bug-fix agent: Azure OpenAI and Claude in Microsoft Foundry

Step 1 of `AZURE-MAPPING.md`. Adds two real model providers behind the existing `ModelGateway`. The default stays the fake adapter, so every existing test still runs offline.

## Facts this prompt relies on

Checked on Microsoft Learn on 11 Nov 2026:

| Fact | Source |
|---|---|
| Azure OpenAI v1 base URL is `https://<resource>.openai.azure.com/openai/v1` (also `https://<resource>.services.ai.azure.com/openai/v1`). No `api-version` parameter is needed. | Learn, "API version lifecycle" |
| With an API key, the documented header is `api-key: <key>`. `Authorization: Bearer` is documented only for Microsoft Entra tokens. | same |
| The `model` field takes the **deployment name**. | same |
| `/chat/completions` exists on v1. | same |
| Claude endpoint is `https://<resource>.services.ai.azure.com/anthropic/v1/messages`. | Learn, "Use Claude models in Microsoft Foundry" |
| Claude headers: `x-api-key: <key>`, `anthropic-version: 2023-06-01`, `Content-Type: application/json`. | same |
| Claude `model` field takes the deployment name (by default the model name, for example `claude-sonnet-4-6`). | same |

Not confirmed by those pages, so the reviewer checks them on the first live call:

- That `/embeddings` is available on the v1 endpoint (the page does not mention it).
- The Claude response shape. The prompt uses Anthropic's public Messages API shape (`content` as a list of blocks, `usage.input_tokens`, `usage.output_tokens`); the Learn page shows no response body.

Account requirements from the Learn page: Claude on Foundry needs a pay-as-you-go subscription (free-trial, student and credit-based subscriptions are not supported), and some Claude models accept Microsoft Entra sign-in only, not API keys.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `issue-intel/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` first.

Do the tasks in order. After each task, append what you did to `issue-intel/PROGRESS.md` under a heading "A1 — Azure models" before starting the next.

## Goal

`ModelGateway` can send chat calls to Azure OpenAI and to Claude in Microsoft Foundry, chosen per model name, with no change to any caller and no change to default behaviour. With default settings the project behaves exactly as it does now.

## Rules

- Do not change the `ModelAdapter` protocol (`complete(model, system, user)`, `embed(model, texts, dim)`) or `AdapterResult`.
- Do not change `ModelGateway.complete`, `embed`, `route_for` or the logging. The only edit in `app/gateway/gateway.py` is inside `_build_adapter`.
- Do not add an SDK. Use `httpx`, as the existing adapter does. Do not add any dependency.
- No test may make a network call. New tests use `httpx.MockTransport`.
- No real key, resource name or price appears anywhere in the code, tests or README. Use placeholders.
- Do not change the embedding dimension, the `Vector(64)` column or any migration.

## Task 1 — settings (`app/settings.py`)

Add, keeping every existing field and default:

```
openai_api_key_header: Literal["bearer", "api-key"] = "bearer"

anthropic_base_url: str = ""            # e.g. https://<resource>.services.ai.azure.com/anthropic
anthropic_api_key: str = ""
anthropic_version: str = "2023-06-01"
anthropic_max_tokens: int = 4096
anthropic_model_prefixes: list[str] = Field(default_factory=lambda: ["claude-"])

model_prices: dict[str, tuple[float, float]] = Field(default_factory=dict)
```

`model_prices` maps a model or deployment name to USD per 1,000 tokens (input, output). It is empty by default.

## Task 2 — adapters (`app/gateway/adapters.py`)

1. **`OpenAICompatAdapter`**
   - `__init__` gains two keyword parameters: `key_header: str = "bearer"` and `transport: httpx.AsyncBaseTransport | None = None`.
   - `_headers()` returns `{"api-key": key}` when `key_header == "api-key"`, otherwise the current `Authorization: Bearer` header.
   - Both `httpx.AsyncClient(...)` calls pass `transport=self._transport`.
   - Nothing else in the class changes.

2. **New class `AnthropicMessagesAdapter`**, placed after `OpenAICompatAdapter`.
   - `__init__(self, base_url: str, api_key: str, version: str, max_tokens: int, timeout_s: float = 120.0, transport: httpx.AsyncBaseTransport | None = None)`.
   - `complete(model, system, user)`: `POST {base_url}/v1/messages` with headers `x-api-key`, `anthropic-version`, `content-type: application/json`, and body:
     ```
     {"model": model, "max_tokens": self._max_tokens, "system": system,
      "messages": [{"role": "user", "content": user}]}
     ```
     Call `raise_for_status()`. The reply text is the concatenation of `block["text"]` for every item of `payload["content"]` whose `"type"` is `"text"`. `tokens_in` is `payload["usage"]["input_tokens"]`, `tokens_out` is `payload["usage"]["output_tokens"]`, each defaulting to 0 if absent. Measure `latency_ms` the same way the OpenAI adapter does.
   - `embed(...)`: raise `NotImplementedError("Claude has no embeddings endpoint; route the embed task to an OpenAI-compatible model")`.

3. **New class `RoutedAdapter`**, placed after it.
   - `__init__(self, default: ModelAdapter, by_prefix: list[tuple[str, ModelAdapter]])`.
   - `complete(model, system, user)`: the first adapter whose prefix `model` starts with handles the call; otherwise `default`.
   - `embed(model, texts, dim)`: same selection rule.
   - It holds no other state and does no logging.

4. **`price_of`**: add an optional third source. New signature `price_of(model, tokens_in, tokens_out, overrides: dict[str, tuple[float, float]] | None = None)`. Look up `overrides` first, then `PRICES`, then the existing default rate. Existing callers that pass three arguments keep working.

## Task 3 — wiring (`app/gateway/gateway.py`, `_build_adapter` only, plus the `price_of` calls)

- When `model_adapter == "openai"`: build the `OpenAICompatAdapter` with `key_header=self._settings.openai_api_key_header`. If `anthropic_base_url` is non-empty, also build an `AnthropicMessagesAdapter` from the four `anthropic_*` settings and return `RoutedAdapter(default=<openai adapter>, by_prefix=[(p, <anthropic adapter>) for p in anthropic_model_prefixes])`. If it is empty, return the OpenAI adapter alone, as now.
- When `model_adapter == "fake"`: unchanged.
- Every existing `price_of(...)` call in this file passes `self._settings.model_prices` as `overrides`. Change nothing else on those lines.

Because the choice is made per model name inside the adapter, the gateway's existing fallback, shadow and canary logic work across providers without modification. Do not add provider logic to the gateway.

## Task 4 — tests (new file `tests/test_gateway_providers.py`)

Use `httpx.MockTransport` with a handler that records the request and returns a canned JSON reply. Follow the style of `tests/test_gateway_fake.py`.

1. OpenAI adapter, default header mode: the request has `Authorization: Bearer k` and no `api-key` header; URL ends with `/chat/completions`; the result text and token counts come from the canned reply.
2. OpenAI adapter, `key_header="api-key"`: the request has `api-key: k` and **no** `Authorization` header.
3. Anthropic adapter: URL is `<base>/v1/messages`; headers `x-api-key` and `anthropic-version: 2023-06-01` are present; the JSON body has `system` as a top-level string, `max_tokens`, and exactly one message with role `user`; a reply with two text blocks and one non-text block yields the two texts concatenated; token counts come from `usage`.
4. Anthropic adapter `embed` raises `NotImplementedError`.
5. `RoutedAdapter`: with prefix `claude-`, model `claude-x` goes to the second adapter and model `gpt-x` goes to the default. Use two `FakeAdapter` instances and inspect their `calls`.
6. Gateway fallback across providers: a `ModelGateway` given a `RoutedAdapter` whose default adapter raises and whose `claude-` adapter succeeds, with a route whose primary is a non-Claude name and whose fallback is a `claude-` name, returns the Claude adapter's text. Build the route the way `tests/test_routing.py` does; if that needs a database, write this test against the adapter and gateway objects directly with the static `task_models` table and say in `PROGRESS.md` what you could not cover.
7. `price_of` uses an override when one is given and the built-in table when it is not.
8. `Settings()` with no environment variables has `model_adapter == "fake"`, `openai_api_key_header == "bearer"` and `anthropic_base_url == ""`.

## Task 5 — README (`issue-intel/README.md`)

Add a section "Running against Azure (optional)" with:

- A table of the environment variables (all prefixed `ISSUEINTEL_`): `MODEL_ADAPTER=openai`, `OPENAI_BASE_URL=https://<resource>.openai.azure.com/openai/v1`, `OPENAI_API_KEY`, `OPENAI_API_KEY_HEADER=api-key`, `ANTHROPIC_BASE_URL=https://<resource>.services.ai.azure.com/anthropic`, `ANTHROPIC_API_KEY`, `TASK_MODELS` (JSON mapping each task type to a deployment name), `MODEL_PRICES` (JSON).
- One example `TASK_MODELS` value that sends `fix_plan`, `fix_patch` and `final_check` to a `claude-` deployment and everything else to OpenAI deployments, with obviously fake deployment names.
- Three plain statements: model names are **deployment names**; embeddings stay at 64 dimensions for now because the adapter keeps the first 64 values of whatever the model returns; evals run with real models cost money and their numbers must be labelled with the model names used.
- Nothing about how to create Azure resources.

## Finish

End with a short report: each task done or not done, files changed, and anything in this prompt that could not be done as written. Never say a test or check passes; you have not run it.
