"""Tests for Jarvis v1 — the tool layer and the brain's tool loop.

No network, no real API key: provider traffic runs on MockTransport.
"""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.brain import (
    TOOLS_UNSUPPORTED_NOTE,
    BrainError,
    OpenAICompatibleBrain,
)
from app.config import Settings
from app.main import create_app
from app.memory import SessionStore
from app.tools import TOOLS, Tool, ToolContext, run_tool, tool_definitions

LIVE_STATUS = {
    "status": "ok",
    "name": "VEGA",
    "provider": "openai",
    "brain": "live",
    "mode": "live",
    "model": "gpt-4o-mini",
}


@pytest.fixture()
def live_ctx():
    return ToolContext(demo=False, status=dict(LIVE_STATUS))


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        settings=Settings(provider="demo"),
        store=SessionStore(tmp_path / "sessions.json"),
    )
    return TestClient(app)


def run(name, args, ctx):
    """run_tool + parse — every result must be valid JSON."""
    out = run_tool(name, args, ctx)
    assert isinstance(out, str)
    return json.loads(out)


# -- definitions ----------------------------------------------------------


def test_definitions_cover_the_three_tools_in_openai_format():
    defs = tool_definitions()
    names = {d["function"]["name"] for d in defs}
    assert names == {
        "get_current_datetime",
        "get_project_todos",
        "get_system_status",
    }
    for d in defs:
        assert d["type"] == "function"
        assert d["function"]["description"]
        assert d["function"]["parameters"]["type"] == "object"


# -- the tools themselves ---------------------------------------------------


def test_datetime_tool_defaults_to_christians_timezone(live_ctx):
    result = run("get_current_datetime", {}, live_ctx)
    assert result["timezone"] == "America/Los_Angeles"
    assert result["date"] and result["time"] and result["iso"]


def test_datetime_tool_accepts_another_timezone(live_ctx):
    result = run(
        "get_current_datetime", {"timezone": "Europe/London"}, live_ctx
    )
    assert result["timezone"] == "Europe/London"


def test_datetime_tool_unknown_timezone_is_a_friendly_error(live_ctx):
    result = run(
        "get_current_datetime", {"timezone": "Nowhere/Special"}, live_ctx
    )
    assert "error" in result
    assert "Nowhere/Special" in result["error"]


def test_todos_tool_returns_the_labelled_snapshot(live_ctx):
    result = run("get_project_todos", {}, live_ctx)
    assert "STATIC SNAPSHOT" in result["source"]  # honestly labelled
    assert result["snapshot_date"]
    names = {p["name"] for p in result["projects"]}
    assert "Age of Elandor" in names
    assert all(p["status"] and p["next_step"] for p in result["projects"])


def test_status_tool_echoes_the_health_payload(live_ctx):
    result = run("get_system_status", {}, live_ctx)
    assert result == LIVE_STATUS


# -- fail-safe behaviour ------------------------------------------------------


def test_unknown_tool_is_a_friendly_error_not_a_crash(live_ctx):
    result = run("launch_the_missiles", {}, live_ctx)
    assert "error" in result
    assert "launch_the_missiles" in result["error"]


def test_non_dict_arguments_are_tolerated(live_ctx):
    result = run("get_current_datetime", None, live_ctx)
    assert result["timezone"] == "America/Los_Angeles"


def test_a_crashing_tool_returns_an_error_without_internals(
    live_ctx, monkeypatch
):
    def boom(ctx, args):
        raise RuntimeError("kaboom-internal-detail")

    monkeypatch.setitem(
        TOOLS,
        "boom",
        Tool(name="boom", description="", parameters={}, handler=boom),
    )
    result = run("boom", {}, live_ctx)
    assert "error" in result
    assert "kaboom" not in result["error"]  # no stack trace, no internals


# -- demo mode never fakes ------------------------------------------------------


def test_demo_mode_tools_return_the_note_not_data():
    ctx = ToolContext(demo=True, status=dict(LIVE_STATUS))
    for name in (
        "get_current_datetime",
        "get_project_todos",
        "get_system_status",
    ):
        result = run(name, {}, ctx)
        assert result["demo"] is True
        assert "Connect a brain" in result["note"]
        assert "projects" not in result  # no snapshot leaks into demo


# -- the brain's tool loop ---------------------------------------------------


def _tool_calling_transport(final_text="Handled, Christian."):
    """First request -> a tool call; second -> the final text."""
    calls = {"bodies": []}

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        calls["bodies"].append(body)
        if len(calls["bodies"]) == 1:
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_1",
                                        "type": "function",
                                        "function": {
                                            "name": "get_current_datetime",
                                            "arguments": (
                                                '{"timezone": '
                                                '"Europe/London"}'
                                            ),
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                },
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": final_text}}
                ]
            },
        )

    return httpx.MockTransport(handler), calls


def test_brain_runs_the_tool_loop(live_ctx):
    transport, calls = _tool_calling_transport()
    brain = OpenAICompatibleBrain(
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        model="gpt-4o-mini",
        provider="openai",
        transport=transport,
    )
    runner = lambda name, args: run_tool(name, args, live_ctx)  # noqa: E731
    reply = brain.reply(
        [{"role": "user", "content": "what time is it in London?"}],
        tools=tool_definitions(),
        tool_runner=runner,
    )
    assert reply == "Handled, Christian."
    first, second = calls["bodies"]
    assert "tools" in first  # definitions went out with the request
    tool_msgs = [m for m in second["messages"] if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0]["tool_call_id"] == "call_1"
    result = json.loads(tool_msgs[0]["content"])
    assert result["timezone"] == "Europe/London"  # args were parsed


def test_brain_falls_back_when_the_model_cannot_do_tools(live_ctx):
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        if "tools" in body:
            return httpx.Response(
                400, json={"error": {"message": "tools unsupported"}}
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "plain"}}
                ]
            },
        )

    brain = OpenAICompatibleBrain(
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        model="some-model",
        provider="openai",
        transport=httpx.MockTransport(handler),
    )
    reply = brain.reply(
        [{"role": "user", "content": "hi"}],
        tools=tool_definitions(),
        tool_runner=lambda name, args: run_tool(name, args, live_ctx),
    )
    assert reply.startswith("plain")  # chat still works
    assert TOOLS_UNSUPPORTED_NOTE in reply  # and she says hands are off


def test_brain_gives_up_on_an_endless_tool_loop(live_ctx):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "c",
                                    "type": "function",
                                    "function": {
                                        "name": "get_system_status",
                                        "arguments": "{}",
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
        )

    brain = OpenAICompatibleBrain(
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        model="gpt-4o-mini",
        provider="openai",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(BrainError):
        brain.reply(
            [{"role": "user", "content": "status?"}],
            tools=tool_definitions(),
            tool_runner=lambda name, args: run_tool(name, args, live_ctx),
        )


# -- through the HTTP API ---------------------------------------------------


def test_chat_endpoint_runs_a_tool_call(tmp_path):
    transport, _calls = _tool_calling_transport("Status checked.")
    brain = OpenAICompatibleBrain(
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        model="gpt-4o-mini",
        provider="openai",
        transport=transport,
    )
    app = create_app(
        settings=Settings(provider="openai", api_key="test-key"),
        brain=brain,
        store=SessionStore(tmp_path / "sessions.json"),
    )
    client = TestClient(app)
    body = client.post(
        "/api/chat", json={"message": "what time is it?", "session_id": "s"}
    ).json()
    assert body["reply"] == "Status checked."
    assert body["brain"] == "live"


def test_health_lists_the_tools(client):
    body = client.get("/api/health").json()
    assert body["tools"] == [
        "get_current_datetime",
        "get_project_todos",
        "get_system_status",
    ]
    assert body["voice"] == "browser"
