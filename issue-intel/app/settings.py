"""Application settings. Env prefix: ISSUEINTEL_."""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ISSUEINTEL_", extra="ignore")

    database_url: str = "postgresql+asyncpg://issueintel:issueintel@localhost:5433/issueintel"
    model_adapter: Literal["openai", "fake"] = "fake"

    # OpenAI-compatible endpoint (only used when model_adapter == "openai").
    openai_base_url: str = "http://localhost:4000/v1"
    openai_api_key: str = "not-a-real-key"
    openai_api_key_header: Literal["bearer", "api-key"] = "bearer"
    openai_chat_model_small: str = "tessera-small"
    openai_chat_model_large: str = "tessera-large"
    openai_embed_model: str = "tessera-embed"
    openai_embed_dim: int = 64

    # Claude in Microsoft Foundry (only used when model_adapter == "openai"
    # and anthropic_base_url is non-empty).
    anthropic_base_url: str = ""  # e.g. https://<resource>.services.ai.azure.com/anthropic
    anthropic_api_key: str = ""
    anthropic_version: str = "2023-06-01"
    anthropic_max_tokens: int = 4096
    anthropic_model_prefixes: list[str] = Field(default_factory=lambda: ["claude-"])

    # USD per 1,000 tokens (input, output) by model or deployment name.
    model_prices: dict[str, tuple[float, float]] = Field(default_factory=dict)

    # Static task-type -> model table (G0-G3; G4 replaces it with versioned routing).
    task_models: dict[str, str] = Field(
        default_factory=lambda: {
            "ticket_parse": "tessera-small",
            "module_check": "tessera-small",
            "relevance": "tessera-small",
            "synthesis": "tessera-large",
            "outcome_classify": "tessera-small",
            "fix_plan": "tessera-large",
            "fix_patch": "tessera-large",
            "conflict_resolve": "tessera-large",
            "quality_verify": "tessera-small",
            "final_check": "tessera-large",
            "embed": "tessera-embed",
        }
    )

    embedding_dim: int = 64
    fix_allowlist: list[str] = Field(
        default_factory=lambda: ["VersionControl", "Localization", "UiState"]
    )
    fix_confidence_threshold: float = 0.7
    fix_max_cycles: int = 3
    fix_token_budget: int = 200000
    sandbox_root: str = "sandboxes"
    sample_repo_path: str = "sample_repo"
    approval_secret: str = "dev-only-secret-change-me"
    approval_token_ttl_seconds: int = 900
    shadow_model: str | None = None
    shadow_share: float = 0.0


def get_settings() -> Settings:
    return Settings()
