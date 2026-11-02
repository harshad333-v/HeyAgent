"""Minimal provider-neutral chat service with explicit cloud-provider selection."""
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
    """Calls one configured provider; never silently forwards to another provider."""

    def __init__(self, *, provider: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout_seconds: float = 45.0) -> None:
        self.provider = (provider or os.getenv("ARYA_DEFAULT_PROVIDER", "gemini")).lower()
        self.api_key = api_key or self._key_for(self.provider)
        self.model = model or os.getenv("ARYA_CHAT_MODEL") or self._default_model(self.provider)
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
                        json={"model": self.model,
                              "messages": [{"role": m.role, "content": m.content} for m in messages]},
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                else:
                    prompt = "\n\n".join(f"{m.role.upper()}: {m.content}" for m in messages)
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                        params={"key": self.api_key},
                        json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
                    )
                    response.raise_for_status()
                    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderRequestFailed("The AI provider request failed.") from exc
        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestFailed("The AI provider returned an empty response.")
        return {"provider": self.provider, "model": self.model, "content": content.strip()}
