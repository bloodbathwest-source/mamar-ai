"""MAMAR's web app — FastAPI factory + routers.

Run it with::

    uvicorn app.main:app --reload

Endpoints:
    GET  /            the chat page
    GET  /api/health  status, provider, mode (demo/live), model
    POST /api/chat    {message, session_id?} -> {reply, session_id, mode}
    POST /api/reset   {session_id} -> clears that session's memory
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .brain import Brain, BrainError, build_brain
from .config import Settings, load_settings
from .memory import HISTORY_SENT_TO_BRAIN, SessionStore
from .persona import load_persona

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "sessions.json"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None


class ResetRequest(BaseModel):
    session_id: str = Field(min_length=1)


def build_router(brain: Brain, store: SessionStore, persona: str,
                 settings: Settings) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "name": "MAMAR",
            "provider": settings.provider,
            "mode": "live" if brain.name != "demo" else "demo",
            "model": settings.effective_model if brain.name != "demo" else None,
        }

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
            reply = brain.reply(messages)
        except BrainError as exc:
            reply = f"⚠️ {exc}"
        store.append(session_id, "user", req.message)
        store.append(session_id, "assistant", reply)
        return {
            "reply": reply,
            "session_id": session_id,
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

    app = FastAPI(title="MAMAR", version="1.0.0")
    app.include_router(build_router(brain, store, persona, settings))

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
