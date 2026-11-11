from app.pipeline.cost import Pricing, embedding_cost_usd, legacy_mt_cost_usd, llm_cost_usd
from app.settings import Settings


def test_llm_cost():
    assert llm_cost_usd(1000, 500, input_per_1k_usd=1.0, output_per_1k_usd=2.0) == 2.0
    assert llm_cost_usd(0, 0, input_per_1k_usd=1.0, output_per_1k_usd=2.0) == 0.0
    assert llm_cost_usd(250, 0, input_per_1k_usd=4.0, output_per_1k_usd=0.0) == 1.0


def test_embedding_and_mt_cost():
    assert embedding_cost_usd(1000, per_1k_usd=0.02) == 0.02
    assert legacy_mt_cost_usd(1000, per_char_usd=0.00002) == 0.02


def test_pricing_from_settings():
    settings = Settings(
        chat_price_per_1k_input_usd=1.0,
        chat_price_per_1k_output_usd=2.0,
        embedding_price_per_1k_usd=0.02,
        legacy_mt_price_per_char_usd=0.00002,
    )
    pricing = Pricing.from_settings(settings)
    assert (pricing.chat_in_per_1k_usd, pricing.chat_out_per_1k_usd) == (1.0, 2.0)
    assert (pricing.embedding_per_1k_usd, pricing.legacy_mt_per_char_usd) == (0.02, 0.00002)


def test_pricing_defaults_to_zero():
    pricing = Pricing.from_settings(Settings())
    assert pricing == Pricing()
