"""VEGA's persona lives in `persona.md` at the project root.

That file *is* her personality — it is read at startup and sent to the
model as the system prompt. Edit the file, restart, she's different.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PERSONA_PATH = PROJECT_ROOT / "persona.md"

FALLBACK_PERSONA = (
    "You are VEGA, a cyberpunk-flavoured personal AI assistant. "
    "Be sharp, direct, and helpful, and never fake a capability you do not have."
)


def load_persona(path: Path | None = None) -> str:
    """Return the persona text, or a minimal fallback if the file is gone."""
    path = DEFAULT_PERSONA_PATH if path is None else Path(path)
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return FALLBACK_PERSONA
    return text or FALLBACK_PERSONA
