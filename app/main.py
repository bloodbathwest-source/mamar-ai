"""VEGA's web app — FastAPI factory + routers.

Run it with::

    uvicorn app.main:app --reload

Endpoints:
    GET  /            the chat page (Jarvis v1: mic input + spoken replies)
    GET  /api/health  status, provider, brain (local/live/demo), model, tools
    POST /api/chat    {message, session_id?} -> {reply, session_id, brain, mode}
    POST /api/reset   {session_id} -> clears that session's memory

Jarvis v1 wiring: when the brain is an OpenAI-compatible one, the chat
route hands it the tool definitions from ``app/tools.py`` plus a
runner bound to a per-request ``ToolContext``. Demo and test brains
are called plainly — they never see tools.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .brain import Brain, BrainError, OpenAICompatibleBrain, build_brain
from .config import Settings, load_settings
from .memory import HISTORY_SENT_TO_BRAIN, SessionStore
from .persona import load_persona
from .tools import TOOLS, ToolContext, run_tool, tool_definitions

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "sessions.json"

# Appended to the persona when a tool-capable brain is wired in, so she
# knows her hands exist and what their limits are. Kept out of
# persona.md: the hands are a property of this build, not her character.
TOOLS_PERSONA_NOTE = (
    "\n\n## Your hands (Jarvis tools)\n\n"
    "You have three real tools wired in, and you may call them "
    "mid-conversation: get_current_datetime (the current date and "
    "time), get_project_todos (Christian's project to-do list), and "
    "get_system_status (which brain you are running on). Use them "
    "when Christian asks about the time, his projects, or your own "
    "status — and report exactly what they return. The to-do list is "
    "a hand-maintained snapshot, not live data; say so when you quote "
    "it. If a tool returns an error, relay it plainly instead of "
    "guessing.\n"
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None


class ResetRequest(BaseModel):
    session_id: str = Field(min_length=1)


def build_router(brain: Brain, store: SessionStore, persona: str,
                 settings: Settings) -> APIRouter:
    router = APIRouter(prefix="/api")

    def brain_kind() -> str:
        """local = brain on this machine (Ollama); live = cloud; demo."""
        if brain.name == "demo":
            return "demo"
        return "local" if settings.local else "live"

    def status_payload() -> dict:
        """Her system status — served by /api/health AND the
        get_system_status tool, so the two can never disagree."""
        return {
            "status": "ok",
            "name": "VEGA",
            "provider": settings.provider,
            "brain": brain_kind(),
            "mode": "live" if brain.name != "demo" else "demo",
            "model": settings.effective_model if brain.name != "demo" else None,
            "tools": sorted(TOOLS),
            "voice": "browser",  # Jarvis v1: speech lives in the page
        }

    @router.get("/health")
    def health() -> dict:
        return status_payload()

    @router.post("/chat")
    def chat(req: ChatRequest) -> dict:
        session_id = req.session_id or uuid.uuid4().hex
        history = store.history(session_id)
        messages = (
            [{"role": "system", "content": persona}]
            + history[-HISTORY_SENT_TO_BRAIN:]
            + [{"role": "user", "content": req.message}]
        )
        try:
            if isinstance(brain, OpenAICompatibleBrain):
                context = ToolContext(
                    demo=False, status=status_payload()
                )
                reply = brain.reply(
                    messages,
                    tools=tool_definitions(),
                    tool_runner=lambda name, args: run_tool(
                        name, args, context
                    ),
                )
            else:
                reply = brain.reply(messages)
        except BrainError as exc:
            reply = f"⚠️ {exc}"
        store.append(session_id, "user", req.message)
        store.append(session_id, "assistant", reply)
        return {
            "reply": reply,
            "session_id": session_id,
            "brain": brain_kind(),
            "mode": "live" if brain.name != "demo" else "demo",
        }

    @router.post("/reset")
    def reset(req: ResetRequest) -> dict:
        store.reset(req.session_id)
        return {"ok": True, "session_id": req.session_id}

    return router


def create_app(
    settings: Settings | None = None,
    brain: Brain | None = None,
    store: SessionStore | None = None,
    persona: str | None = None,
) -> FastAPI:
    """App factory — every dependency can be injected (tests do)."""
    settings = settings if settings is not None else load_settings()
    brain = brain if brain is not None else build_brain(settings)
    store = store if store is not None else SessionStore(DEFAULT_DATA_FILE)
    persona = persona if persona is not None else load_persona()
    if isinstance(brain, OpenAICompatibleBrain):
        # A tool-capable brain gets told it has hands. Demo/test brains
        # are never told — they can't call tools, and she must not
        # claim capabilities she doesn't have in that mode.
        persona = persona + TOOLS_PERSONA_NOTE

    app = FastAPI(title="VEGA", version="1.1.0")
    app.include_router(build_router(brain, store, persona, settings))

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
