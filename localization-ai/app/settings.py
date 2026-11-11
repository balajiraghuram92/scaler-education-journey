"""Environment configuration for the localization-ai service.

Every field maps to the UPPER_SNAKE_CASE environment variable of the same
name (pydantic-settings). No model name is hard-coded anywhere else: the
chat/embedding/COMET model names below are the only place they appear.

Database connection, either shape (same idea as ai-agent/config.py):
  * ``DATABASE_URL`` (libpq URI or ``key=value`` string).
  * ``DATABASE_HOST``, ``DATABASE_NAME``, ``DATABASE_USER``,
    ``DATABASE_PASSWORD`` and optional ``DATABASE_PORT`` (default 5432).
``DATABASE_URL`` wins when both shapes are present.
"""

from pydantic_settings import BaseSettings
from psycopg.conninfo import make_conninfo


class Settings(BaseSettings):
    database_url: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "studytracker"
    database_user: str = "studyuser"
    database_password: str = ""

    # Shared secret for the x-api-key header. Must match the .NET side
    # (LocalizationAi:SharedSecret). Empty refuses to start / always 401s.
    api_shared_secret: str = ""

    # "fake" runs with no model at all; "openai-compat" talks to a vLLM
    # server or any OpenAI-compatible endpoint.
    chat_provider: str = "fake"
    chat_base_url: str = "http://localhost:8001/v1"
    chat_api_key: str = ""
    chat_model: str = "qwen2.5-7b-instruct"
    chat_timeout_seconds: float = 60.0

    embedding_provider: str = "fake"
    embedding_base_url: str = "http://localhost:8001/v1"
    embedding_api_key: str = ""
    embedding_model: str = "bge-small-en-v1.5"
    embedding_dimensions: int = 384

    # COMET-Kiwi reference-free quality model. Only used when comet_enabled
    # is true AND requirements-comet.txt is installed; otherwise runs record
    # null for the COMET metric and nothing else fails.
    comet_enabled: bool = False
    comet_model: str = "Unbabel/wmt22-cometkiwi-da"
    comet_gpus: int = 0

    # Semantic-cache cosine-similarity threshold (0..1): at or above is a hit.
    cache_similarity_threshold: float = 0.95

    # Prices for the cost-governance story. Zeros mean "rate not configured":
    # set your real or amortized rates (e.g. GPU cost per token, Google's
    # per-character rate) so ledger entries are meaningful.
    chat_price_per_1k_input_usd: float = 0.0
    chat_price_per_1k_output_usd: float = 0.0
    embedding_price_per_1k_usd: float = 0.0
    legacy_mt_price_per_char_usd: float = 0.0

    enable_docs: bool = False

    def database_conninfo(self) -> str:
        """Return a libpq conninfo string from DATABASE_URL or DATABASE_* parts."""
        if self.database_url and self.database_url.strip():
            return self.database_url.strip()
        return make_conninfo(
            host=self.database_host,
            port=str(self.database_port),
            dbname=self.database_name,
            user=self.database_user,
            password=self.database_password,
        )
