from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections import Counter
from collections.abc import AsyncIterator, Callable
from contextlib import aclosing
from dataclasses import dataclass, field

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

Upstream = Callable[[str], AsyncIterator[str]]


@dataclass(slots=True)
class StreamMetrics:
    ttft_ms: list[float] = field(default_factory=list)
    outcomes: Counter[str] = field(default_factory=Counter)


def sse(data: dict | str, event: str | None = None) -> bytes:
    payload = data if isinstance(data, str) else json.dumps(data)
    head = f"event: {event}\n" if event else ""
    return f"{head}data: {payload}\n\n".encode()


PING = b": ping\n\n"


class ChatIn(BaseModel):
    prompt: str = Field(min_length=1)


def create_app(upstream: Upstream, *, ping_interval_s: float = 15.0, deadline_s: float = 60.0,
               clock: Callable[[], float] = time.monotonic) -> tuple[FastAPI, StreamMetrics]:
    app = FastAPI()
    metrics = StreamMetrics()

    async def events(prompt: str, request_id: str) -> AsyncIterator[bytes]:
        started = clock()
        yield sse({"request_id": request_id}, event="meta")
        tokens_sent = 0
        outcome = "ok"
        try:
            async with asyncio.timeout(deadline_s):
                async with aclosing(upstream(prompt)) as tokens:
                    it = aiter(tokens)
                    pending: asyncio.Future[str] | None = None
                    try:
                        while True:
                            pending = asyncio.ensure_future(anext(it))
                            while True:
                                done, _ = await asyncio.wait({pending}, timeout=ping_interval_s)
                                if done:
                                    break
                                yield PING                          # keep proxies and clients alive
                            try:
                                token = pending.result()
                            except StopAsyncIteration:
                                break
                            pending = None
                            if tokens_sent == 0:
                                metrics.ttft_ms.append((clock() - started) * 1000)
                            tokens_sent += 1
                            yield sse({"delta": token})
                    finally:
                        if pending is not None and not pending.done():
                            pending.cancel()                        # let the upstream see the cancellation
                            await asyncio.gather(pending, return_exceptions=True)
            yield sse({"tokens": tokens_sent}, event="done")
        except TimeoutError:
            outcome = "deadline"
            yield sse({"code": "deadline_exceeded", "request_id": request_id}, event="error")
        except asyncio.CancelledError:
            outcome = "disconnected"
            raise
        except Exception:
            outcome = "error"
            yield sse({"code": "upstream_failed", "request_id": request_id}, event="error")
        finally:
            metrics.outcomes[outcome] += 1

    @app.post("/chat/stream")
    async def chat_stream(body: ChatIn) -> StreamingResponse:
        return StreamingResponse(
            events(body.prompt, uuid.uuid4().hex[:8]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app, metrics
