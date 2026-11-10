
from typing import Sequence

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from ..core.config import Config


settings = Config()


def generate_response(
    system_prompt: str,
    user_prompt: str,
    message_history: Sequence[ModelMessage] | None = None
) -> str:

    if not settings.GROQ_API_KEY.get_secret_value():
        raise ValueError("GROQ_API_KEY is not configured")

    provider = GroqProvider(
        api_key=settings.GROQ_API_KEY.get_secret_value()
    )

    model = GroqModel(
        settings.GROQ_MODEL,
        provider=provider
    )

    agent = Agent(
        model,
        instructions=system_prompt,
        output_type=str
    )

    result = agent.run_sync(
        user_prompt,
        message_history=list(message_history or []),
        model_settings={
            "max_tokens": 1024,
            "temperature": 0.2
        }
    )

    response = result.output.strip()

    if not response:
        raise ValueError("Groq returned an empty response")

    return response
