"""MAMAR's configuration — everything comes from environment variables.

Copy `.env.example` to `.env`, fill it in, and either export the values in
your shell or load them with your process manager. No API key ever lives
in code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Default API address + model per provider. OpenAI and xAI both speak the
# same "OpenAI-compatible" chat API, so one adapter serves both — only
# these two values change.
PROVIDER_DEFAULTS = {
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "xai": {"base_url": "https://api.x.ai/v1", "model": "grok-4"},
}

LIVE_PROVIDERS = tuple(PROVIDER_DEFAULTS.keys())


@dataclass
class Settings:
    provider: str = "demo"
    api_key: str = ""
    model: str = ""
    base_url: str = ""

    @property
    def live(self) -> bool:
        """True when a real provider brain can run (provider + key set)."""
        return self.provider in LIVE_PROVIDERS and bool(self.api_key)

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
        provider=(env.get("MAMAR_PROVIDER") or "demo").strip().lower(),
        api_key=(env.get("MAMAR_API_KEY") or "").strip(),
        model=(env.get("MAMAR_MODEL") or "").strip(),
        base_url=(env.get("MAMAR_BASE_URL") or "").strip(),
    )
