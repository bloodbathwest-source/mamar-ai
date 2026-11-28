"""Conversation memory — one JSON file, one entry per session.

Deliberately simple: the whole store is a dict of
``session_id -> [ {role, content}, ... ]`` persisted to
``data/sessions.json`` (gitignored — these are private conversations).
Writes go to a temp file and are renamed over the old one, so a crash
mid-write can't corrupt the store.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

MAX_MESSAGES_PER_SESSION = 100  # hard cap so the file can't grow forever
HISTORY_SENT_TO_BRAIN = 20  # how many past messages accompany each new turn


class SessionStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._sessions: dict[str, list[dict]] = {}
        self._load()

    # -- persistence -----------------------------------------------------

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if isinstance(data, dict):
            self._sessions = {
                str(k): list(v) for k, v in data.items() if isinstance(v, list)
            }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._sessions, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    # -- API --------------------------------------------------------------

    def history(self, session_id: str) -> list[dict]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            msgs = self._sessions.setdefault(session_id, [])
            msgs.append({"role": role, "content": content})
            del msgs[:-MAX_MESSAGES_PER_SESSION]  # keep only the newest
            self._save()

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            self._save()
