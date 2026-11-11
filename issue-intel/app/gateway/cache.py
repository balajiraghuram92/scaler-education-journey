"""Result cache (in-process LRU) and batch mode (DB job queue)."""
from __future__ import annotations

import hashlib
from collections import OrderedDict
from typing import Any

from sqlalchemy import select

from app.governance.rls import service_session
from app.models.g2 import Job


def cache_key(task: str, model: str, system: str, user: str) -> str:
    return hashlib.sha256(
        f"{task}\n{model}\n{system}\n{user}".encode()
    ).hexdigest()


class ResultCache:
    def __init__(self, cap: int = 1000) -> None:
        self._cap = cap
        self._items: OrderedDict[str, tuple[str, int, int]] = OrderedDict()

    def get(self, key: str) -> tuple[str, int, int] | None:
        if key not in self._items:
            return None
        self._items.move_to_end(key)
        return self._items[key]

    def set(self, key: str, value: tuple[str, int, int]) -> None:
        self._items[key] = value
        self._items.move_to_end(key)
        while len(self._items) > self._cap:
            self._items.popitem(last=False)


async def enqueue_batch(calls: list[dict[str, Any]]) -> int:
    """Queue non-urgent calls; the worker runs them together."""
    async with service_session() as session:
        job = Job(kind="batch_call", payload={"calls": calls, "results": []})
        session.add(job)
        await session.commit()
        return job.id


async def batch_results(job_id: int) -> list[dict[str, Any]] | None:
    async with service_session() as session:
        job = await session.get(Job, job_id)
        if job is None or job.status != "DONE":
            return None
        results = job.payload.get("results", [])
        return list(results)


async def execute_batch_job(job_id: int, gateway: Any) -> None:
    from app.gateway.tasks import TaskType

    async with service_session() as session:
        job = await session.get(Job, job_id)
        if job is None:
            return
        job.status = "RUNNING"
        await session.commit()
        calls = list(job.payload.get("calls", []))
    results: list[dict[str, Any]] = []
    try:
        for call in calls:
            result = await gateway.complete(
                TaskType(call["task"]), system=call["system"], user=call["user"],
                data=call.get("data"), run_id=call.get("run_id"),
                module=call.get("module"),
            )
            results.append({"text": result.text, "model": result.model,
                            "tokens_in": result.tokens_in,
                            "tokens_out": result.tokens_out,
                            "cost_usd": result.cost_usd})
    except Exception as exc:
        async with service_session() as session:
            job = await session.get(Job, job_id)
            if job is not None:
                job.status = "FAILED"
                job.error = f"{type(exc).__name__}: {exc}"
                await session.commit()
        return
    async with service_session() as session:
        job = await session.get(Job, job_id)
        if job is not None:
            job.status = "DONE"
            payload = dict(job.payload)
            payload["results"] = results
            job.payload = payload
            await session.commit()
