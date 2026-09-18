from pydantic import BaseModel
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider 
from config import MUSE_AI_API_KEY

class EchoResult(BaseModel):
    message: str

model = OpenAIChatModel(
        "muse-spark-1.3",
        provider=OpenAIProvider(
            base_url="https://api.meta.ai/v1",
            api_key=MUSE_AI_API_KEY,
            ),
            )

echo_agent = Agent(
    model=model,
    output_type= PromptedOutput(EchoResult),
    system_prompt="You are a helpful assistant that echoes back the user's message.")