from pydantic import BaseModel
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from config import Settings


class EchoResult(BaseModel):
    message: str


def build_echo_agent(settings: Settings) -> Agent:
    """Scaffold agent on Muse (model id and base URL come from config)."""
    model = OpenAIChatModel(
        settings.muse_model,
        provider=OpenAIProvider(
            base_url=settings.muse_base_url,
            api_key=settings.muse_api_key,
        ),
    )
    return Agent(
        model=model,
        # Muse rejects forced tool_choice, so use prompted (not tool) output.
        output_type=PromptedOutput(EchoResult),
        model_settings={"timeout": settings.llm_timeout_seconds},
        system_prompt="You are a helpful assistant that echoes back the user's message.",
    )
