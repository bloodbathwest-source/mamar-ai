# MAMAR.AI – Matrix AI Machine Agents Rebel

> **Cyberpunk AI chatbot** — and now, real code.
> MAMAR started life as a no-code app (see *Previously* below). This repo
> is her rebuild: a small, working personal AI assistant that Christian
> owns outright — her chat page, her personality, and her memory live
> here, and her *brain* is rented from an AI provider's API.

---

## How a "clone of Muse" works, in plain language

Muse (Meta's assistant) isn't one magic thing — it's three parts
stacked together. This rebuild copies that shape with open parts:

1. **The interface** — the part you touch. Here: a chat web page, a
   server that remembers your conversation, and a persona file that
   tells the AI who it is. *This is the part in this repo, and it's the
   part that makes her MAMAR instead of a generic chatbot.*
2. **The brain** — a big AI model (like GPT or Grok). Nobody sane trains
   one of these at home; you **rent** it. Your server sends the
   conversation to the provider's API and gets the reply back. Swap the
   provider in one config file and she thinks with a different brain.
3. **The persona** — `persona.md`. One editable text file, sent to the
   model with every conversation, that says who MAMAR is and how she
   talks. Edit the file, restart, new personality.

So: **MAMAR = this app + a provider API key.** The app is hers forever;
the brain is a subscription you can change.

---

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # then open .env and add your API key
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** and talk to her.

### Configuration (.env)

| Setting | What it does |
|---|---|
| `MAMAR_PROVIDER` | `openai`, `xai`, or `demo` |
| `MAMAR_API_KEY` | Your key from that provider — the one thing that makes her real |
| `MAMAR_MODEL` | Optional. Defaults: `gpt-4o-mini` (OpenAI), `grok-4` (xAI) |
| `MAMAR_BASE_URL` | Optional. Only for a different OpenAI-compatible host |

OpenAI and xAI speak the same API dialect, so one adapter serves both —
switching her brain from GPT to Grok is changing two lines in `.env`.

> 🔑 **Your `.env` is gitignored and must stay that way.** This repo is
> public; a committed key is a stolen key. See
> [EXPORT-SAFETY.md](EXPORT-SAFETY.md).

### Demo mode

No key? She still runs. Without an API key MAMAR answers with canned,
in-character replies that are **clearly labelled `[DEMO MODE]`** and tell
you a key is needed for real answers. She never fakes being a live model.

### A straight word about "uncensored"

MAMAR's personality is hers — but what the *model* will and won't say is
set by whichever provider supplies the brain, not by this code. Every
provider draws its own lines, and they differ: of the providers MAMAR
names, **xAI's Grok is generally the most permissive**, OpenAI and
Anthropic are stricter, and none of them is limit-free. Picking a
provider is picking a set of limits — the persona file controls her
style, not their rules.

---

## Project layout

```
app/
  main.py     FastAPI app factory + routes (/, /api/chat, /api/health, /api/reset)
  brain.py    The adapter layer: one interface, OpenAI-compatible + demo brains
  config.py   Settings from environment variables
  persona.py  Loads persona.md as the system prompt
  memory.py   Per-session conversation history in data/sessions.json
static/       The chat page (plain HTML/CSS/JS, no build step)
persona.md    MAMAR's personality — edit this to change who she is
tests/        pytest suite (no network, no real key needed)
data/         Her memory file lives here at runtime (gitignored)
```

## Tests

```bash
pytest
```

Covers the health endpoint, demo-mode replies, persona loading, session
memory (two turns remember context; reset forgets), and the adapter's
request shape against a mocked provider.

---

## Previously…

MAMAR was originally built on the no-code platforms **Bubble** and
**Base44**, with the mamar.ai domain pointed at the platform version.
The platform exports were never committed to this repo — the old README
described a Quick Start whose files didn't exist here. That history, the
export-safety checklist, and the showcase notes live on the
`sofia-fix-pass` branch (PR #2). This rebuild replaces the no-code
direction with code Christian owns; [EXPORT-SAFETY.md](EXPORT-SAFETY.md)
still applies to anything exported from the old platforms.
