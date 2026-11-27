"""VEGA's hands — a small, safe tool layer (Jarvis v1).

A *tool* is a plain function with a JSON contract: the brain (an
OpenAI-compatible model with function calling) may ask for one
mid-conversation, the server runs it, and the JSON result goes back to
the brain as a ``tool`` message. The registry below is the whole list
of things her hands can do in v1 — all read-only, all local:

- ``get_current_datetime`` — the current date and time.
- ``get_project_todos`` — Christian's project to-do summary, read from
  ``project_todos.json`` in the project root. That file is a **static
  snapshot**, maintained by hand — it says so inside the file, and the
  tool result carries the labelling through.
- ``get_system_status`` — which brain she is running on (the same
  payload ``GET /api/health`` returns).

Safety rules, matching the rest of the app:

- ``run_tool`` **never raises**. Unknown tools, bad arguments, and
  handler crashes all come back as a JSON ``{"error": ...}`` with a
  friendly, in-character message — never a stack trace.
- **Demo mode never fakes tool results.** With no live brain wired in,
  every tool returns an honestly-labelled demo note saying a brain
  needs connecting. (The demo brain is canned and never calls tools at
  all; this gate is defence in depth.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TODO_FILE = PROJECT_ROOT / "project_todos.json"

# Christian is in Salem, Oregon — his wall clock is the default.
DEFAULT_TIMEZONE = "America/Los_Angeles"

DEMO_TOOL_NOTE = (
    "Demo mode: no live brain is connected, so I can't run my tools "
    "for real. Connect a brain — an OpenAI or xAI API key, or a local "
    "Ollama — and my hands switch on."
)


@dataclass
class ToolContext:
    """What a tool is allowed to know about the running app."""

    demo: bool = True
    # Same payload GET /api/health returns; get_system_status serves it.
    status: dict = field(default_factory=dict)


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    handler: Callable[[ToolContext, dict], dict]

    def definition(self) -> dict:
        """This tool in OpenAI function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


_NO_ARGS = {"type": "object", "properties": {}, "additionalProperties": False}


def _current_datetime(ctx: ToolContext, args: dict) -> dict:
    tz_name = str(args.get("timezone") or DEFAULT_TIMEZONE)
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return {
            "error": (
                f"I don't know a timezone called {tz_name!r} — try an "
                "IANA name like 'America/New_York' or 'Europe/London'."
            )
        }
    now = datetime.now(tz)
    return {
        "timezone": tz_name,
        "date": now.strftime("%A, %B %d, %Y"),
        "time": now.strftime("%I:%M %p"),
        "iso": now.isoformat(timespec="seconds"),
    }


def _project_todos(ctx: ToolContext, args: dict) -> dict:
    try:
        data = json.loads(TODO_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "error": (
                "My project to-do file (project_todos.json) isn't "
                "readable right now, so I can't quote it — and I won't "
                "guess at what's on Christian's list."
            )
        }
    if not isinstance(data, dict):
        return {
            "error": (
                "My project to-do file is in a shape I don't recognise, "
                "so I won't quote it."
            )
        }
    return data


def _system_status(ctx: ToolContext, args: dict) -> dict:
    return dict(ctx.status)


TOOLS: dict[str, Tool] = {
    tool.name: tool
    for tool in (
        Tool(
            name="get_current_datetime",
            description=(
                "Get the current date and time. Defaults to Christian's "
                "timezone (America/Los_Angeles); pass an IANA timezone "
                "name to ask about somewhere else."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone name, e.g. 'Europe/London'.",
                    }
                },
                "additionalProperties": False,
            },
            handler=_current_datetime,
        ),
        Tool(
            name="get_project_todos",
            description=(
                "Read Christian's project to-do summary: his projects, "
                "their status, and next steps. NOTE: this is a static "
                "snapshot maintained by hand (project_todos.json), not "
                "live data — say so when quoting it."
            ),
            parameters=_NO_ARGS,
            handler=_project_todos,
        ),
        Tool(
            name="get_system_status",
            description=(
                "Report VEGA's own system status: which provider and "
                "model she is running on, and whether her brain is "
                "local, live (cloud), or demo."
            ),
            parameters=_NO_ARGS,
            handler=_system_status,
        ),
    )
}


def tool_definitions() -> list[dict]:
    """All tools in the format an OpenAI-compatible brain expects."""
    return [tool.definition() for tool in TOOLS.values()]


def run_tool(name: str, arguments: dict | None, context: ToolContext) -> str:
    """Run one tool and return its result as a JSON string.

    Never raises: every failure is a JSON ``{"error": ...}`` with a
    friendly message the brain can relay. In demo mode every tool
    returns the honestly-labelled demo note instead of data.
    """
    if context.demo:
        return json.dumps({"demo": True, "note": DEMO_TOOL_NOTE})
    tool = TOOLS.get(name)
    if tool is None:
        return json.dumps(
            {
                "error": (
                    f"I don't have a tool called {name!r}. My tools "
                    f"are: {', '.join(sorted(TOOLS))}."
                )
            }
        )
    if not isinstance(arguments, dict):
        arguments = {}
    try:
        result = tool.handler(context, arguments)
    except Exception:  # a glitching hand must never crash the chat
        return json.dumps(
            {
                "error": (
                    f"My {name} tool glitched and returned nothing — "
                    "no result, and I won't invent one. Try again in "
                    "a moment."
                )
            }
        )
    return json.dumps(result)
