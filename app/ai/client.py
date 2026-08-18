from dataclasses import dataclass

import httpx

from app.config import get_settings


@dataclass(slots=True)
class AIMessage:
    role: str
    content: str


class AIClient:
    """
    Клиент OpenAI-compatible Chat Completions API.

    Поддерживает OpenAI, Ollama и другие совместимые API.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        settings = get_settings()

        self.base_url = (
            base_url or settings.llm_base_url
        ).rstrip("/")

        self.api_key = (
            api_key
            if api_key is not None
            else settings.llm_api_key
        )

        self.model = model or settings.llm_model

        if not self.model:
            raise ValueError("LLM_MODEL is not configured")

        self.timeout = (
            timeout
            if timeout is not None
            else settings.llm_timeout_seconds
        )

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.8,
        max_tokens: int = 500,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
        ) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(
                "Invalid LLM response format"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM returned an empty response")

        return content.strip()
