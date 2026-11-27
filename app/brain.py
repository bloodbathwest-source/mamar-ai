"""VEGA's brain — an adapter layer over AI provider APIs.

VEGA does not contain a model. Her *interface* (this app: chat page,
persona, memory) is hers; her *brain* is rented from a provider API.
Every brain implements one method::

    reply(messages, tools=None, tool_runner=None) -> str

``messages`` is the OpenAI-style list: system prompt first, then the
conversation history, then the newest user message. ``tools`` /
``tool_runner`` are the Jarvis v1 hands (see ``app/tools.py``): tool
definitions in OpenAI function-calling format, plus a callable the
brain invokes when the model asks for a tool. Brains that can't call
tools ignore both.

Two implementations:

- ``OpenAICompatibleBrain`` — talks to any provider that speaks the
  OpenAI chat-completions API. OpenAI and xAI (Grok) both do, so the
  same adapter serves either; only base URL, key, and model change
  (see ``app/config.py``). Ollama speaks the same API from the user's
  own machine, so it uses this adapter too — with no API key and no
  Authorization header.
- ``DemoBrain`` — used when no provider is configured. Its replies are
  canned, in character, and **clearly labelled as demo mode**. It never
  pretends to be a real model answer.
"""

from __future__ import annotations

import json
from typing import Callable

import httpx

from .config import Settings

DEMO_LABEL = "[DEMO MODE]"

OLLAMA_DOWN_MESSAGE = (
    "my local brain isn't answering — Ollama doesn't seem to be running "
    "on this machine. Start it (open the Ollama app, or run "
    "`ollama serve`), make sure my model is downloaded "
    "(`ollama pull llama3.1:8b`), and ask me again. No key, no cloud — "
    "the brain has to actually be awake down there."
)


class BrainError(Exception):
    """The provider call failed; the message is safe to show the user."""


class _ToolsRejected(Exception):
    """The provider refused the request because it carried tools.

    Some models behind an OpenAI-compatible API can't do function
    calling and answer HTTP 400 when ``tools`` is present. The brain
    catches this and retries without tools, so chat still works.
    """


# How many tool rounds one reply may take before the brain gives up —
# a model that keeps asking for tools forever must not loop forever.
MAX_TOOL_ROUNDS = 5

TOOLS_UNSUPPORTED_NOTE = (
    "(House note: this brain doesn't do tool-calling, so my hands are "
    "off with it — connect a tool-capable model, like gpt-4o-mini, "
    "grok-4, or llama3.1, and I can check the time, Christian's project "
    "list, and my own status mid-conversation.)"
)


class Brain:
    """Interface every brain implements."""

    name = "base"

    def reply(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_runner: Callable[[str, dict], str] | None = None,
    ) -> str:  # pragma: no cover
        raise NotImplementedError


class DemoBrain(Brain):
    """Canned, honestly-labelled replies for when no API key is set."""

    name = "demo"

    _LINES = [
        "I hear you — but right now I'm running on canned lines, not a live "
        "model. Add an API key (OpenAI or xAI) to my .env file — or point "
        "me at a local Ollama brain — and I'll answer for real.",
        "That's a question for the real me. This is the demo shell talking: "
        "no key, no brain — just good posture and neon.",
        "Noted. If I had my provider key wired in, I'd dig into that "
        "properly. Until then, everything I say is a placeholder like this.",
    ]

    def __init__(self) -> None:
        self._turn = 0

    def reply(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_runner: Callable[[str, dict], str] | None = None,
    ) -> str:
        # Canned lines never call tools — demo mode must not fake
        # tool results (see app/tools.py for the matching gate).
        line = self._LINES[self._turn % len(self._LINES)]
        self._turn += 1
        return f"{DEMO_LABEL} {line}"


class OpenAICompatibleBrain(Brain):
    """Calls ``{base_url}/chat/completions``.

    Sends a bearer Authorization header only when an API key is set —
    a local brain (Ollama) has no key and gets no header.
    ``unreachable_message`` replaces the generic connection-error text;
    the local brain uses it to say, in character, "start Ollama".
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str = "",
        model: str,
        provider: str = "openai",
        transport: httpx.BaseTransport | None = None,
        timeout: float = 60.0,
        unreachable_message: str | None = None,
        trust_env: bool = True,
    ) -> None:
        self.name = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._transport = transport
        self._timeout = timeout
        self._unreachable_message = unreachable_message
        # A local brain must be reached directly: proxy settings from the
        # environment (HTTP_PROXY etc.) never apply to 127.0.0.1 — and a
        # malformed one can crash client construction outright.
        self._trust_env = trust_env

    def reply(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_runner: Callable[[str, dict], str] | None = None,
    ) -> str:
        """One reply — with a tool-calling loop when tools are wired.

        When the model answers with ``tool_calls`` instead of text,
        each call is run through ``tool_runner`` and the JSON result
        goes back to the model as a ``tool`` message, until the model
        produces text (or ``MAX_TOOL_ROUNDS`` is hit). If the provider
        rejects the tools outright (HTTP 400 — a model without
        function calling), the request is retried bare: chat still
        works, and the reply carries a note that her hands are off
        with this brain.
        """
        use_tools = bool(tools) and tool_runner is not None
        tools_rejected = False
        convo = list(messages)
        for _round in range(MAX_TOOL_ROUNDS + 1):
            payload: dict = {"model": self.model, "messages": convo}
            if use_tools:
                payload["tools"] = tools
            try:
                message = self._complete(payload)
            except _ToolsRejected:
                # Start the turn over, bare: a model that refuses tools
                # may also choke on the tool messages already exchanged.
                use_tools = False
                tools_rejected = True
                convo = list(messages)
                continue
            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                text = message.get("content") or ""
                if tools_rejected:
                    text = f"{text}\n\n{TOOLS_UNSUPPORTED_NOTE}".strip()
                return text
            convo.append(message)  # the assistant turn carrying the calls
            for call in tool_calls:
                fn = call.get("function") or {}
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except (ValueError, TypeError):
                    args = {}
                if not isinstance(args, dict):
                    args = {}
                result = tool_runner(str(fn.get("name") or ""), args)
                convo.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", ""),
                        "content": result,
                    }
                )
        raise BrainError(
            "I got tangled in my own tool calls — too many rounds "
            "without an answer. Ask me again, simpler."
        )

    def _complete(self, payload: dict) -> dict:
        """POST one chat-completions request; return the message dict."""
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            with httpx.Client(
                transport=self._transport,
                timeout=self._timeout,
                trust_env=self._trust_env,
            ) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if "tools" in payload and exc.response.status_code == 400:
                raise _ToolsRejected from exc
            raise BrainError(
                f"my provider ({self.name}) answered with an error: "
                f"HTTP {exc.response.status_code}. Check the API key and "
                "model name in .env."
            ) from exc
        except httpx.ConnectError as exc:
            if self._unreachable_message:
                raise BrainError(self._unreachable_message) from exc
            raise BrainError(
                f"I couldn't reach my provider ({self.name}): {exc}. "
                "Check the network and VEGA_BASE_URL."
            ) from exc
        except httpx.HTTPError as exc:
            raise BrainError(
                f"I couldn't reach my provider ({self.name}): {exc}. "
                "Check the network and VEGA_BASE_URL."
            ) from exc
        try:
            return response.json()["choices"][0]["message"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise BrainError(
                f"my provider ({self.name}) sent back a reply I couldn't "
                "parse."
            ) from exc


def build_brain(
    settings: Settings,
    transport: httpx.BaseTransport | None = None,
) -> Brain:
    """Pick the brain the settings describe — demo unless fully wired.

    A selected local provider (Ollama) is always "wired": no key needed.
    If Ollama itself isn't running, the brain says so at chat time with
    a friendly error instead of silently falling back to demo.
    """
    if settings.live:
        return OpenAICompatibleBrain(
            base_url=settings.effective_base_url,
            api_key=settings.api_key,
            model=settings.effective_model,
            provider=settings.provider,
            transport=transport,
            unreachable_message=(
                OLLAMA_DOWN_MESSAGE if settings.local else None
            ),
            trust_env=not settings.local,
        )
    return DemoBrain()
