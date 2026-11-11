"""Token/character cost helpers. Pure functions; rates come from settings."""

from dataclasses import dataclass

from app.settings import Settings


@dataclass(frozen=True)
class Pricing:
    chat_in_per_1k_usd: float = 0.0
    chat_out_per_1k_usd: float = 0.0
    embedding_per_1k_usd: float = 0.0
    legacy_mt_per_char_usd: float = 0.0

    @classmethod
    def from_settings(cls, settings: Settings) -> "Pricing":
        return cls(
            chat_in_per_1k_usd=settings.chat_price_per_1k_input_usd,
            chat_out_per_1k_usd=settings.chat_price_per_1k_output_usd,
            embedding_per_1k_usd=settings.embedding_price_per_1k_usd,
            legacy_mt_per_char_usd=settings.legacy_mt_price_per_char_usd,
        )


def llm_cost_usd(input_tokens: int, output_tokens: int, *, input_per_1k_usd: float, output_per_1k_usd: float) -> float:
    """Chat cost for a call: tokens/1000 * the configured per-1k rates."""
    return input_tokens / 1000 * input_per_1k_usd + output_tokens / 1000 * output_per_1k_usd


def embedding_cost_usd(tokens: int, *, per_1k_usd: float) -> float:
    """Embedding cost for a call: tokens/1000 * the configured rate."""
    return tokens / 1000 * per_1k_usd


def legacy_mt_cost_usd(characters: int, *, per_char_usd: float) -> float:
    """Legacy MT cost: characters * the configured per-character rate."""
    return characters * per_char_usd
