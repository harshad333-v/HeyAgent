"""Provider-neutral chat service for explicitly selected cloud providers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence

import httpx


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str


class ProviderNotConfigured(RuntimeError):
    pass


class ProviderRequestFailed(RuntimeError):
    pass


class ChatService:
    """Calls exactly one configured provider; never silently falls back."""

    def __init__(self, *, provider: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout_seconds: float = 45.0) -> None:
        configured_default = os.getenv("ARYA_DEFAULT_PROVIDER", "gemini").lower()
        self.provider = (provider or configured_default).lower()
        self.api_key = api_key if api_key is not None else self._key_for(self.provider)
        model_env = {"gemini": "GEMINI_CHAT_MODEL", "openai": "OPENAI_CHAT_MODEL"}.get(self.provider)
        provider_model = os.getenv(model_env, "") if model_env else ""
        legacy_model = os.getenv("ARYA_CHAT_MODEL", "") if self.provider == configured_default else ""
        self.model = model or provider_model or legacy_model or self._default_model(self.provider)
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _key_for(provider: str) -> str:
        names = {"gemini": "GEMINI_API_KEY", "openai": "OPENAI_API_KEY"}
        return os.getenv(names.get(provider, "ARYA_UNKNOWN_PROVIDER_KEY"), "")

    @staticmethod
    def _default_model(provider: str) -> str:
        return {"gemini": "gemini-2.5-flash", "openai": "gpt-4.1-mini"}.get(provider, "")

    async def complete(self, messages: Sequence[ChatMessage]) -> dict[str, str]:
        if self.provider not in {"gemini", "openai"}:
            raise ProviderNotConfigured("Configured provider is not supported.")
        if not self.api_key:
            raise ProviderNotConfigured(f"No API key configured for {self.provider}.")
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                if self.provider == "openai":
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={"model": self.model, "messages": [
                            {"role": message.role, "content": message.content} for message in messages
                        ]},
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                else:
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                        headers={"x-goog-api-key": self.api_key},
                        json={"contents": [
                            {"role": "model" if message.role == "assistant" else "user",
                             "parts": [{"text": message.content}]}
                            for message in messages
                        ]},
                    )
                    response.raise_for_status()
                    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderRequestFailed("The AI provider request failed.") from exc
        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestFailed("The AI provider returned an empty response.")
        return {"provider": self.provider, "model": self.model, "content": content.strip()}
