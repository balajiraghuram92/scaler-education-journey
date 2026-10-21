from __future__ import annotations

import gc
import weakref
from functools import lru_cache
from itertools import count


class Session:
    __slots__ = ("tenant", "_prompts", "__weakref__")

    def __init__(self, tenant: str) -> None:
        self.tenant = tenant
        self._prompts: dict[str, str] = {}

    def render_prompt(self, name: str) -> str:
        try:
            return self._prompts[name]
        except KeyError:
            rendered = self._prompts[name] = f"[{self.tenant}] {name}"
            return rendered


class SessionRegistry:
    def __init__(self) -> None:
        self._sessions: weakref.WeakValueDictionary[int, Session] = (
            weakref.WeakValueDictionary()
        )
        self._ids = count(1)

    def register(self, session: Session) -> int:
        sid = next(self._ids)
        self._sessions[sid] = session
        return sid

    def get(self, sid: int) -> Session | None:
        return self._sessions.get(sid)

    def __len__(self) -> int:
        return len(self._sessions)
