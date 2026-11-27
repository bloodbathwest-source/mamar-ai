# Export Safety Checklist — read this BEFORE committing any Bubble / Base44 export

This repo is **public**. The original no-code build was wired to five paid
API services — **Tavily, OpenAI, xAI, Anthropic, ElevenLabs** — and
platform exports can quietly include the API keys for them. If a key is committed to a public repo, strangers can find
it (bots scan GitHub for keys within minutes) and run up bills on those
accounts.

Run through this list every time, before `git commit`. It takes two minutes.

---

## 1. Export the app

- **Bubble:** `Settings → General → Export app` → downloads a JSON file.
  Save it under `bubble/` (e.g. `bubble/export-2026-11-26.json`).
- **Base44:** `Project → Export` → downloads a ZIP file.
  Save it under `base44/`.

## 2. Search the export for keys BEFORE committing

Open the export file in any text editor (for a ZIP, unzip it first) and use
**Find** (Ctrl+F / Cmd+F) for each of these. Any hit next to a long random-
looking string of characters is a red flag:

- `sk-` ← how OpenAI and Anthropic keys start
- `api_key`
- `apikey`
- `api key`
- `token`
- `secret`
- `password`
- `Bearer`
- The five service names: `Tavily`, `OpenAI`, `xAI`, `Anthropic`, `ElevenLabs`
  — check what is written next to each one.
- Also search for the first 6–8 characters of each of your real keys, if you
  know them — that catches keys stored under names nobody would guess.

## 3. If you find a key in the export

- **Delete the key value** from the export file (leave the setting name, remove
  the actual key), or re-export after moving the key so it only lives in the
  platform's **Settings → API** page, which is where keys belong.
- Never "fix" it by renaming the file or moving it to a subfolder — if the
  file is committed, the key is public, whatever it is called.
- Double-check the repo's `.gitignore` covers the file type you just exported,
  and add a pattern if it doesn't.

## 4. If a key ever lands in a public commit — act immediately

**Deleting the file afterwards is NOT enough.** Git keeps history, and copies
and scans happen within minutes.

1. Go to that service's dashboard (OpenAI / Anthropic / xAI / Tavily /
   ElevenLabs) and **revoke / rotate the key** — create a new one and delete
   the old one. Do this first, before anything else.
2. Put the new key into the platform's Settings → API page only.
3. Then clean up the repo.

A rotated key is a dead key — once it is revoked, whatever leaked is useless.

## 5. Then commit

Only after steps 2–4 come back clean:

```bash
git add .
git commit -m "Describe the change"
git push origin main
```

When in doubt, stop and check first. A two-minute search is cheaper than a
hijacked API account.
