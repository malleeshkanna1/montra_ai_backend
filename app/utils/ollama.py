
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from ..core.config import Config


settings = Config()


def generate_response(
    system_prompt: str,
    user_prompt: str
) -> str:

    provider = OllamaProvider(
        base_url=settings.OLLAMA_BASE_URL
    )

    model = OllamaModel(
        settings.OLLAMA_MODEL,
        provider=provider
    )

    agent = Agent(
        model,
        instructions=system_prompt,
        output_type=str
    )

    result = agent.run_sync(
        user_prompt,
        model_settings={
            "max_tokens": 1024,
            "temperature": 0.2,
            "extra_body": {
                "options": {
                    "num_ctx": 8192
                }
            }
        }
    )

    response = result.output.strip()

    if not response:
        raise ValueError("Ollama returned an empty response")

    return response
