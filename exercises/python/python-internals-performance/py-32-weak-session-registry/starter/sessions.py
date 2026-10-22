from __future__ import annotations


class Session:
    """One object per tenant connection.

    Requirements:
    - uses ``__slots__`` (no ``__dict__``, so new attributes raise AttributeError) and supports weak references
      (``"__weakref__"`` must be one of the slots)
    - ``render_prompt(name)`` returns ``f"[{tenant}] {name}"`` and caches the result PER INSTANCE (the second call for
      the same name returns the identical string object). The cache must not hold a reference to the session
      itself, so do not use ``functools.lru_cache`` on the method.
    """

    def __init__(self, tenant: str) -> None:
        raise NotImplementedError("Implement Session.__init__")

    def render_prompt(self, name: str) -> str:
        raise NotImplementedError("Implement Session.render_prompt")


class SessionRegistry:
    """Looks sessions up by id WITHOUT keeping them alive."""

    def __init__(self) -> None:
        raise NotImplementedError("Implement SessionRegistry.__init__")

    def register(self, session: Session) -> int:
        """Return a new id; ids start at 1 and increase."""
        raise NotImplementedError("Implement register")

    def get(self, sid: int) -> Session | None:
        """The live session, or None once it has been garbage collected (or never existed)."""
        raise NotImplementedError("Implement get")

    def __len__(self) -> int:
        """Number of sessions still alive."""
        raise NotImplementedError("Implement __len__")
