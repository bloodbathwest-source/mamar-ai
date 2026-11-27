# VEGA — Christian's personal AI assistant

> **Cyberpunk AI chatbot** — and now, real code.
> VEGA started life as a no-code app (see *Previously* below). This repo
> is her rebuild: a small, working personal AI assistant that Christian
> owns outright — her chat page, her personality, and her memory live
> here, and her *brain* is rented from an AI provider's API.
>
> *Formerly called **MAMAR** (Matrix AI Machine Agents Rebel) —
> Christian renamed her **VEGA**, for the brightest star in Lyra, on
> 2026-11-26. The GitHub repo still carries the old name (`mamar-ai`)
> until he renames it in GitHub settings; everything in the code has
> already made the move.*

---

## How a "clone of Muse" works, in plain language

Muse (Meta's assistant) isn't one magic thing — it's three parts
stacked together. This rebuild copies that shape with open parts:

1. **The interface** — the part you touch. Here: a chat web page, a
   server that remembers your conversation, and a persona file that
   tells the AI who it is. *This is the part in this repo, and it's the
   part that makes her VEGA instead of a generic chatbot.*
2. **The brain** — a big AI model (like GPT or Grok). Nobody sane trains
   one of these at home; you **rent** it from a provider's API — or run
   a free open model on your own machine (see *Run her brain locally*
   below). Your server sends the conversation to the brain and gets the
   reply back. Swap the provider in one config file and she thinks with
   a different brain.
3. **The persona** — `persona.md`. One editable text file, sent to the
   model with every conversation, that says who VEGA is and how she
   talks. Edit the file, restart, new personality.

So: **VEGA = this app + a provider API key.** The app is hers forever;
the brain is a subscription you can change.

---

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # then open .env: add a cloud API key, or pick the local Ollama brain
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** and talk to her.

### Configuration (.env)

| Setting | What it does |
|---|---|
| `VEGA_PROVIDER` | `openai`, `xai`, `ollama` (local), or `demo` |
| `VEGA_API_KEY` | Your key from that provider — the one thing that makes her real in the cloud. **Not needed for `ollama`.** |
| `VEGA_MODEL` | Optional. Defaults: `gpt-4o-mini` (OpenAI), `grok-4` (xAI), `llama3.1:8b` (Ollama) |
| `VEGA_BASE_URL` | Optional. Only for a different OpenAI-compatible host |

OpenAI and xAI speak the same API dialect, so one adapter serves both —
switching her brain from GPT to Grok is changing two lines in `.env`.
Ollama speaks it too, from your own machine.

> 🔑 **Your `.env` is gitignored and must stay that way.** This repo is
> public; a committed key is a stolen key. See
> [EXPORT-SAFETY.md](EXPORT-SAFETY.md).

### Demo mode

No provider configured? She still runs. With no cloud API key and no
local provider selected, VEGA answers with canned, in-character replies
that are **clearly labelled `[DEMO MODE]`** and tell you what would make
her real. She never fakes being a live model — and if Ollama is selected
but not running, she says that instead of quietly dropping into demo.

---

## Jarvis v1 — voice + hands 🎙️

VEGA with a voice and a small set of hands, in the shape of a certain
movie butler: **voice + brain + tools**, all in the browser + this app.

**Voice in.** Tap the 🎤 button in the message box and talk. This uses
the browser's built-in speech recognition (the Web Speech API) — no
server speech-to-text, no new dependencies. It works in **Chrome and
Edge**; in a browser without it, the mic button says so instead of
failing quietly. The words land in the message box and send like typing.
Typing always works — voice is an extra, never a requirement.

**Voice out.** The **🔊 voice** toggle in the header makes VEGA speak
her replies aloud (browser speech synthesis, a suitable English voice
picked automatically). While it's on, a **JARVIS MODE** badge lights up
next to her status. The choice is remembered between visits.

**Hands (tools).** With a tool-capable brain wired in, VEGA can call
three read-only tools mid-conversation (`app/tools.py`):

| Tool | What it does |
|---|---|
| `get_current_datetime` | The current date and time (Christian's timezone by default) |
| `get_project_todos` | His project to-do summary — read from `project_todos.json`, a **static snapshot** maintained by hand, and labelled as one |
| `get_system_status` | Which brain she is running on (the same payload as `/api/health`) |

Function calling works over the same OpenAI-compatible adapter, so
OpenAI, xAI, **and local Ollama** (`llama3.1:8b` supports tools) all get
hands the same way. Tools fail safe: a glitch returns a friendly error
to the brain, never a stack trace — and **demo mode never fakes tool
results**: with no live brain, tools return a "connect a brain" note
instead of data. If a model can't do function calling at all, chat
still works and her reply notes that her hands are off with that brain.

**Honest limits of v1.** No wake word — you tap the mic, she doesn't
listen in the background. Speech recognition is the browser's (in
Chrome that's Google's service, so voice input needs the internet even
with a local brain; speech *output* is fully local). The to-do list is
a snapshot, not a live feed. And the tools are read-only: she can look,
not touch. Calendar, email, and smart-home hands are future work.

---

## Run her brain locally (free, offline) 🖥️

The third option: no cloud, no key, no bills. [Ollama](https://ollama.com)
runs open AI models on your own computer, and it speaks the same API
dialect as OpenAI — so VEGA talks to it through the same adapter, just
pointed at your machine.

1. **Install Ollama** from [ollama.com](https://ollama.com) (Windows,
   macOS, Linux).
2. **Download the model** (about 4.7 GB, one time):
   ```bash
   ollama pull llama3.1:8b
   ```
   `qwen2.5:7b` is a good alternative pick — same steps, swap the name.
3. **Make sure Ollama is running** — open the Ollama app, or run
   `ollama serve` in a terminal. It listens on
   `http://127.0.0.1:11434`.
4. **Point VEGA at it** in `.env`:
   ```
   VEGA_PROVIDER=ollama
   VEGA_MODEL=llama3.1:8b
   ```
   (No `VEGA_API_KEY` — there is nothing to authenticate. The chat
   page badge will read **LOCAL BRAIN (OLLAMA)**.)
5. **Run VEGA** as usual (`uvicorn app.main:app`) and talk to her.

**Honest expectations.** An 8-billion-parameter local model is
*noticeably* less capable than GPT/Claude-class cloud brains — shorter
memory for nuance, weaker reasoning, the odd confident mistake. In
exchange it runs **entirely on your machine**: no per-message cost, no
API key, works with the Wi-Fi unplugged, and nothing you say leaves the
house. Its filtering is only whatever the open model's makers baked in
— there is no provider watching the conversation, because there is no
provider. `llama3.1:8b` fits comfortably on a 16 GB RAM machine with a
modern GPU (e.g. an RTX 5060 laptop).

**Making the brain *hers*.** A stock open model is still a stranger
wearing VEGA's persona file. The future step is **fine-tuning**:
training the open model on examples of how VEGA should talk and what
she should know, until the personality lives in the model itself rather
than in a prompt. That is a project of its own — this local setup is
the groundwork it builds on.

### A straight word about "uncensored"

VEGA's personality is hers — but what the *model* will and won't say is
set by whoever supplies the brain, not by this code. Every cloud
provider draws its own lines, and they differ: of the providers VEGA
names, **xAI's Grok is generally the most permissive**, OpenAI and
Anthropic are stricter, and none of them is limit-free. Picking a
provider is picking a set of limits — the persona file controls her
style, not their rules. The **local Ollama brain** is the exception:
the model runs on your own machine, so the only limits in play are the
ones the open model's makers built into the model itself.

---

## Project layout

```
app/
  main.py     FastAPI app factory + routes (/, /api/chat, /api/health, /api/reset)
  brain.py    The adapter layer: one interface, OpenAI-compatible + demo brains
  tools.py    Jarvis v1 hands: the tool registry (time, project to-dos, status)
  config.py   Settings from environment variables
  persona.py  Loads persona.md as the system prompt
  memory.py   Per-session conversation history in data/sessions.json
static/       The chat page (plain HTML/CSS/JS, no build step; mic + voice built in)
persona.md    VEGA's personality — edit this to change who she is
project_todos.json  Hand-maintained snapshot of Christian's projects (the to-do tool reads it)
tests/        pytest suite (no network, no real key needed)
data/         Her memory file lives here at runtime (gitignored)
```

## Tests

```bash
pytest
```

Covers the health endpoint, demo-mode replies, persona loading, session
memory (two turns remember context; reset forgets), the adapter's
request shape against a mocked provider, the local Ollama brain
(keyless selection, no auth header, friendly error when Ollama is down),
and the Jarvis v1 tool layer: each tool's contract, fail-safe errors,
demo mode returning notes instead of data, and the brain's tool-calling
loop (including the no-function-calling fallback) against mocked
providers.

---

## Previously…

She was originally built on the no-code platforms **Bubble** and
**Base44**, with her domain pointed at the platform version.
The platform exports were never committed to this repo — the old README
described a Quick Start whose files didn't exist here. That history, the
export-safety checklist, and the showcase notes live on the
`sofia-fix-pass` branch (PR #2). This rebuild replaces the no-code
direction with code Christian owns; [EXPORT-SAFETY.md](EXPORT-SAFETY.md)
still applies to anything exported from the old platforms.
