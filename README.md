# MAMAR.AI – Matrix AI Machine Agents Rebel

> **Live:** https://mamar.ai  
> **Cyberpunk AI chatbot** that hacks the web in real time and allies with Grok, GPT-4o, Claude.

---

## QUICK START (No-Code)

> **Status:** The `bubble/` and `base44/` export files are **not in this repo yet**, so steps 1–2 currently have nothing to import. Export the app from Bubble/Base44 first (see the workflow table below), save the files under `bubble/` and `base44/`, and commit them — then this Quick Start works as written.

1. **Bubble** – Open [bubble.io](https://bubble.io), import `bubble/export-*.json`  
2. **Base44** – Open [base44.com](https://base44.com), import `base44/export-*.zip`  
3. Add API keys in **Settings → API** (Tavily, OpenAI, xAI Grok, Anthropic, ElevenLabs)  
4. Point **mamar.ai** CNAME to the platform’s URL  
5. Publish → Done

---

## EXPORT / IMPORT WORKFLOW

| Platform | Export | Import |
|----------|--------|--------|
| **Bubble** | `Settings → General → Export app` → JSON | `Dashboard → New app → Import` |
| **Base44** | `Project → Export` → ZIP | `New Project → Import ZIP` |

**Push to GitHub after every major edit:**

```bash
git add .
git commit -m "Add voice mode + Grok alliance"
git push origin main
```

> ⚠️ **Before committing any export, run the [Export Safety Checklist](EXPORT-SAFETY.md).** Exports can contain API keys, and this repo is public.

---

## SEE MAMAR IN ACTION

<!-- ================================================================
     SHOWCASE PLACEHOLDERS — Christian: replace everything in this
     section with real material from the live app.
     1. Take screenshots of MAMAR at mamar.ai (chat window, an answer
        you're proud of, voice mode if it's on).
     2. Save them in a `docs/screenshots/` folder in this repo.
     3. Swap each placeholder line below for the matching screenshot.
     ================================================================ -->

**Screenshots — coming soon.** Placeholders where the real pictures will go:

- *[Screenshot placeholder 1 — MAMAR's main chat screen]*
- *[Screenshot placeholder 2 — MAMAR answering a question]*
- *[Screenshot placeholder 3 — voice mode / extra feature screen]*

**Sample conversation — FORMAT EXAMPLE ONLY.** This is a placeholder showing
how a real chat will be presented here; it is not a transcript. Replace it
with an actual conversation copied from the live app:

> **You:** What's the latest news in AI today?
>
> **MAMAR:** *[Her reply would be pasted here, exactly as she gave it —
> including anything she found on the web while answering.]*
>
> **You:** *[A follow-up question]*
>
> **MAMAR:** *[Her follow-up reply]*
