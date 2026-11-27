"""VEGA's configuration — everything comes from environment variables.

Copy `.env.example` to `.env`, fill it in, and either export the values in
your shell or load them with your process manager. No API key ever lives
in code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Default API address + model per provider. OpenAI and xAI both speak the
# same "OpenAI-compatible" chat API, so one adapter serves both — only
# these two values change. Ollama speaks the same API too, but serves it
# locally (on the user's own machine) instead of from a cloud.
PROVIDER_DEFAULTS = {
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "xai": {"base_url": "https://api.x.ai/v1", "model": "grok-4"},
    "ollama": {"base_url": "http://127.0.0.1:11434/v1", "model": "llama3.1:8b"},
}

LIVE_PROVIDERS = tuple(PROVIDER_DEFAULTS.keys())

# Providers that need no API key — the brain runs on the user's own
# machine, so there is nothing to authenticate against.
KEYLESS_PROVIDERS = ("ollama",)


@dataclass
class Settings:
    provider: str = "demo"
    api_key: str = ""
    model: str = ""
    base_url: str = ""

    @property
    def live(self) -> bool:
        """True when a real provider brain can run.

        Cloud providers need an API key; a local provider (Ollama) needs
        none — selecting it is the whole configuration.
        """
        if self.provider not in LIVE_PROVIDERS:
            return False
        if self.provider in KEYLESS_PROVIDERS:
            return True
        return bool(self.api_key)

    @property
    def local(self) -> bool:
        """True when the brain runs on the user's own machine."""
        return self.provider in KEYLESS_PROVIDERS

    @property
    def effective_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        return PROVIDER_DEFAULTS.get(self.provider, {}).get("base_url", "")

    @property
    def effective_model(self) -> str:
        if self.model:
            return self.model
        return PROVIDER_DEFAULTS.get(self.provider, {}).get("model", "")


def load_settings(env: dict | None = None) -> Settings:
    """Build Settings from the environment (or a dict, for tests)."""
    env = os.environ if env is None else env
    return Settings(
        provider=(env.get("VEGA_PROVIDER") or "demo").strip().lower(),
        api_key=(env.get("VEGA_API_KEY") or "").strip(),
        model=(env.get("VEGA_MODEL") or "").strip(),
        base_url=(env.get("VEGA_BASE_URL") or "").strip(),
    )
