"""Langfuse tracing, initialised lazily.

Importing this module does no I/O. ``init_observability`` is called once from
the app lifespan; it creates the Langfuse client (which reads LANGFUSE_* from
the environment itself) and turns on Pydantic AI instrumentation, but makes no
network call. ``check_auth`` is the explicit, opt-in network check.
"""

import logging

logger = logging.getLogger(__name__)

_client = None
_enabled = False


def init_observability(enabled: bool) -> bool:
    """Set up tracing once. Returns True when Langfuse tracing is active."""
    global _client, _enabled
    if _client is not None or not enabled:
        if not enabled:
            logger.warning("LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY unset: tracing disabled")
        return _enabled

    from langfuse import get_client
    from pydantic_ai import Agent

    _client = get_client()
    Agent.instrument_all()
    _enabled = True
    logger.info("Langfuse tracing enabled")
    return True


def is_enabled() -> bool:
    return _enabled


def langchain_callbacks() -> list:
    """Callback handlers for LangGraph/LangChain runs (empty when tracing is off)."""
    if not _enabled:
        return []
    from langfuse.langchain import CallbackHandler

    return [CallbackHandler()]


def check_auth() -> bool:
    """Network call to Langfuse; for manual diagnostics only, never at startup."""
    return bool(_client is not None and _client.auth_check())


def shutdown_observability() -> None:
    """Flush pending traces on app shutdown."""
    global _client, _enabled
    if _client is not None:
        try:
            _client.shutdown()
        except Exception:  # noqa: BLE001 - shutdown must never raise
            logger.exception("Langfuse shutdown failed")
    _client = None
    _enabled = False
