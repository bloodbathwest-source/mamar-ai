"""MAMAR's brain — an adapter layer over AI provider APIs.

MAMAR does not contain a model. Her *interface* (this app: chat page,
persona, memory) is hers; her *brain* is rented from a provider API.
Every brain implements one method::

    reply(messages: list[dict]) -> str

``messages`` is the OpenAI-style list: system prompt first, then the
conversation history, then the newest user message.

Two implementations:

- ``OpenAICompatibleBrain`` — talks to any provider that speaks the
  OpenAI chat-completions API. OpenAI and xAI (Grok) both do, so the
  same adapter serves either; only base URL, key, and model change
  (see ``app/config.py``).
- ``DemoBrain`` — used when no API key is configured. Its replies are
  canned, in character, and **clearly labelled as demo mode**. It never
  pretends to be a real model answer.
"""

from __future__ import annotations

import httpx

from .config import Settings

DEMO_LABEL = "[DEMO MODE]"


class BrainError(Exception):
    """The provider call failed; the message is safe to show the user."""


class Brain:
    """Interface every brain implements."""

    name = "base"

    def reply(self, messages: list[dict]) -> str:  # pragma: no cover
        raise NotImplementedError


class DemoBrain(Brain):
    """Canned, honestly-labelled replies for when no API key is set."""

    name = "demo"

    _LINES = [
        "I hear you — but right now I'm running on canned lines, not a live "
        "model. Add an API key (OpenAI or xAI) to my .env file and I'll "
        "answer for real.",
        "That's a question for the real me. This is the demo shell talking: "
        "no key, no brain — just good posture and neon.",
        "Noted. If I had my provider key wired in, I'd dig into that "
        "properly. Until then, everything I say is a placeholder like this.",
    ]

    def __init__(self) -> None:
        self._turn = 0

    def reply(self, messages: list[dict]) -> str:
        line = self._LINES[self._turn % len(self._LINES)]
        self._turn += 1
        return f"{DEMO_LABEL} {line}"


class OpenAICompatibleBrain(Brain):
    """Calls ``{base_url}/chat/completions`` with a bearer API key."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        provider: str = "openai",
        transport: httpx.BaseTransport | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.name = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._transport = transport
        self._timeout = timeout

    def reply(self, messages: list[dict]) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(
                transport=self._transport, timeout=self._timeout
            ) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BrainError(
                f"my provider ({self.name}) answered with an error: "
                f"HTTP {exc.response.status_code}. Check the API key and "
                "model name in .env."
            ) from exc
        except httpx.HTTPError as exc:
            raise BrainError(
                f"I couldn't reach my provider ({self.name}): {exc}. "
                "Check the network and MAMAR_BASE_URL."
            ) from exc
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise BrainError(
                f"my provider ({self.name}) sent back a reply I couldn't "
                "parse."
            ) from exc


def build_brain(settings: Settings) -> Brain:
    """Pick the brain the settings describe — demo unless fully wired."""
    if settings.live:
        return OpenAICompatibleBrain(
            base_url=settings.effective_base_url,
            api_key=settings.api_key,
            model=settings.effective_model,
            provider=settings.provider,
        )
    return DemoBrain()
