"""Tests for the VEGA rebuild — no network, no real API key."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.brain import (
    DEMO_LABEL,
    Brain,
    BrainError,
    DemoBrain,
    OpenAICompatibleBrain,
    build_brain,
)
from app.config import Settings, load_settings
from app.main import create_app
from app.memory import SessionStore
from app.persona import FALLBACK_PERSONA, load_persona


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        settings=Settings(provider="demo"),
        store=SessionStore(tmp_path / "sessions.json"),
    )
    return TestClient(app)


# -- health ---------------------------------------------------------------


def test_health_ok_in_demo_mode(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["name"] == "VEGA"
    assert body["mode"] == "demo"


def test_chat_page_is_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "VEGA" in res.text


# -- demo mode --------------------------------------------------------------


def test_demo_chat_reply_is_clearly_labelled(client):
    res = client.post("/api/chat", json={"message": "hello", "session_id": "s1"})
    assert res.status_code == 200
    body = res.json()
    assert body["mode"] == "demo"
    assert body["session_id"] == "s1"
    assert DEMO_LABEL in body["reply"]
    assert "API key" in body["reply"]  # says what would make her real


def test_chat_without_session_id_gets_one(client):
    res = client.post("/api/chat", json={"message": "hi"})
    assert res.status_code == 200
    assert res.json()["session_id"]


# -- persona ------------------------------------------------------------------


def test_persona_file_loads_and_names_her():
    text = load_persona()
    assert "VEGA" in text
    assert "brightest star" in text
    assert "Lyra" in text


def test_persona_missing_file_falls_back(tmp_path):
    assert load_persona(tmp_path / "nope.md") == FALLBACK_PERSONA


# -- session memory -------------------------------------------------------------


class RecordingBrain(Brain):
    """Fake brain that remembers what it was sent and echoes a marker."""

    name = "recording"

    def __init__(self):
        self.calls: list[list[dict]] = []

    def reply(self, messages):
        self.calls.append(messages)
        return f"reply-{len(self.calls)}"


@pytest.fixture()
def memory_client(tmp_path):
    brain = RecordingBrain()
    app = create_app(
        settings=Settings(provider="demo"),
        brain=brain,
        store=SessionStore(tmp_path / "sessions.json"),
        persona="TEST PERSONA",
    )
    return TestClient(app), brain


def test_two_turns_remember_context(memory_client):
    client, brain = memory_client
    client.post("/api/chat", json={"message": "my name is Christian",
                                   "session_id": "abc"})
    client.post("/api/chat", json={"message": "what is my name?",
                                   "session_id": "abc"})
    second_call = brain.calls[1]
    assert second_call[0] == {"role": "system", "content": "TEST PERSONA"}
    contents = [m["content"] for m in second_call]
    assert "my name is Christian" in contents  # first user turn remembered
    assert "reply-1" in contents               # first assistant turn too
    assert contents[-1] == "what is my name?"


def test_sessions_are_isolated(memory_client):
    client, brain = memory_client
    client.post("/api/chat", json={"message": "secret of session one",
                                   "session_id": "one"})
    client.post("/api/chat", json={"message": "hello", "session_id": "two"})
    contents = [m["content"] for m in brain.calls[1]]
    assert "secret of session one" not in contents


def test_reset_clears_memory(memory_client):
    client, brain = memory_client
    client.post("/api/chat", json={"message": "remember this",
                                   "session_id": "abc"})
    res = client.post("/api/reset", json={"session_id": "abc"})
    assert res.json()["ok"] is True
    client.post("/api/chat", json={"message": "fresh start",
                                   "session_id": "abc"})
    contents = [m["content"] for m in brain.calls[-1]]
    assert "remember this" not in contents
    assert contents[-1] == "fresh start"


def test_store_persists_to_disk(tmp_path):
    path = tmp_path / "sessions.json"
    SessionStore(path).append("s", "user", "hello")
    reloaded = SessionStore(path)
    assert reloaded.history("s") == [{"role": "user", "content": "hello"}]


# -- OpenAI-compatible adapter ---------------------------------------------------


def test_adapter_request_shape_and_reply_parsing():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"role": "assistant",
                                            "content": "yo, Christian"}}]},
        )

    brain = OpenAICompatibleBrain(
        base_url="https://api.x.ai/v1",
        api_key="test-key-123",
        model="grok-4",
        provider="xai",
        transport=httpx.MockTransport(handler),
    )
    messages = [
        {"role": "system", "content": "persona"},
        {"role": "user", "content": "hello"},
    ]
    assert brain.reply(messages) == "yo, Christian"
    assert captured["url"] == "https://api.x.ai/v1/chat/completions"
    assert captured["auth"] == "Bearer test-key-123"
    assert captured["body"]["model"] == "grok-4"
    assert captured["body"]["messages"] == messages


# -- Local brain (Ollama) ---------------------------------------------------


def test_ollama_is_live_with_no_api_key():
    settings = load_settings({"VEGA_PROVIDER": "ollama"})
    assert settings.live is True
    assert settings.local is True
    assert settings.api_key == ""
    assert settings.effective_base_url == "http://127.0.0.1:11434/v1"
    assert settings.effective_model == "llama3.1:8b"
    brain = build_brain(settings)
    assert not isinstance(brain, DemoBrain)
    assert brain.name == "ollama"


def test_cloud_provider_without_key_stays_demo():
    settings = load_settings({"VEGA_PROVIDER": "openai"})
    assert settings.live is False
    assert isinstance(build_brain(settings), DemoBrain)


def test_ollama_adapter_sends_no_auth_header():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"role": "assistant",
                                            "content": "local and loud"}}]},
        )

    brain = build_brain(
        load_settings({"VEGA_PROVIDER": "ollama"}),
        transport=httpx.MockTransport(handler),
    )
    reply = brain.reply([{"role": "user", "content": "hello"}])
    assert reply == "local and loud"
    assert captured["url"] == "http://127.0.0.1:11434/v1/chat/completions"
    assert captured["auth"] is None  # no key, no Authorization header
    assert captured["body"]["model"] == "llama3.1:8b"


def _ollama_down_transport(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused", request=request)


def test_ollama_unreachable_raises_friendly_error():
    brain = build_brain(
        load_settings({"VEGA_PROVIDER": "ollama"}),
        transport=httpx.MockTransport(_ollama_down_transport),
    )
    with pytest.raises(BrainError) as excinfo:
        brain.reply([{"role": "user", "content": "hello"}])
    message = str(excinfo.value)
    assert "Ollama" in message
    assert "ollama pull llama3.1:8b" in message


def test_ollama_ignores_proxy_environment(monkeypatch):
    # A local brain is dialled directly: proxy env vars must neither
    # route the request nor crash client construction (a malformed one
    # did exactly that before trust_env was disabled for local brains).
    # Nothing listens on the Ollama port here, so the expected outcome
    # is the friendly BrainError — not an httpx.InvalidURL escaping.
    monkeypatch.setenv("HTTP_PROXY", "http://[::1")
    monkeypatch.setenv("HTTPS_PROXY", "http://[::1")
    brain = build_brain(load_settings({"VEGA_PROVIDER": "ollama"}))
    with pytest.raises(BrainError) as excinfo:
        brain.reply([{"role": "user", "content": "hello"}])
    assert "Ollama" in str(excinfo.value)


def test_ollama_health_reports_local_brain(tmp_path):
    app = create_app(
        settings=load_settings({"VEGA_PROVIDER": "ollama"}),
        store=SessionStore(tmp_path / "sessions.json"),
    )
    body = TestClient(app).get("/api/health").json()
    assert body["provider"] == "ollama"
    assert body["brain"] == "local"
    assert body["mode"] == "live"
    assert body["model"] == "llama3.1:8b"


def test_ollama_down_chat_is_friendly_not_demo(tmp_path):
    brain = build_brain(
        load_settings({"VEGA_PROVIDER": "ollama"}),
        transport=httpx.MockTransport(_ollama_down_transport),
    )
    app = create_app(
        settings=load_settings({"VEGA_PROVIDER": "ollama"}),
        brain=brain,
        store=SessionStore(tmp_path / "sessions.json"),
    )
    body = TestClient(app).post(
        "/api/chat", json={"message": "hello", "session_id": "s1"}
    ).json()
    assert body["brain"] == "local"
    assert body["mode"] == "live"
    assert DEMO_LABEL not in body["reply"]  # no silent demo fallback
    assert "Ollama" in body["reply"]        # says what to do instead
