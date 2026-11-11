"""Provider factories: settings select the fake or the OpenAI-compatible pair."""

from app.providers.base import ChatProvider, EmbeddingProvider
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider
from app.providers.openai_compat import OpenAICompatChatProvider, OpenAICompatEmbeddingProvider
from app.settings import Settings

CHAT_PROVIDERS = ("fake", "openai-compat")
EMBEDDING_PROVIDERS = ("fake", "openai-compat")


def build_chat_provider(settings: Settings) -> ChatProvider:
    if settings.chat_provider == "fake":
        return FakeChatProvider()
    if settings.chat_provider == "openai-compat":
        return OpenAICompatChatProvider(
            base_url=settings.chat_base_url,
            api_key=settings.chat_api_key,
            model=settings.chat_model,
            timeout_seconds=settings.chat_timeout_seconds,
        )
    raise ValueError(f"unknown CHAT_PROVIDER {settings.chat_provider!r}; expected one of {CHAT_PROVIDERS}")


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "fake":
        return FakeEmbeddingProvider(dimensions=settings.embedding_dimensions)
    if settings.embedding_provider == "openai-compat":
        return OpenAICompatEmbeddingProvider(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            timeout_seconds=settings.chat_timeout_seconds,
        )
    raise ValueError(
        f"unknown EMBEDDING_PROVIDER {settings.embedding_provider!r}; expected one of {EMBEDDING_PROVIDERS}"
    )
