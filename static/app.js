// VEGA chat page — plain JS, no build step.
"use strict";

const messagesEl = document.getElementById("messages");
const typingEl = document.getElementById("typing");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send-btn");
const badge = document.getElementById("mode-badge");
const resetBtn = document.getElementById("reset-btn");
const micBtn = document.getElementById("mic-btn");
const voiceBtn = document.getElementById("voice-btn");
const jarvisBadge = document.getElementById("jarvis-badge");

let sessionId = localStorage.getItem("vega-session") || null;

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

async function loadBadge() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (data.mode === "demo") {
      badge.textContent = "DEMO MODE";
      badge.classList.add("demo");
    } else if (data.brain === "local") {
      badge.textContent = ("LOCAL BRAIN (OLLAMA) · " + (data.model || "")).toUpperCase();
    } else {
      badge.textContent = (data.provider + " · " + (data.model || "")).toUpperCase();
    }
  } catch {
    badge.textContent = "OFFLINE";
    badge.classList.add("demo");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMessage("user", text);
  typingEl.classList.remove("hidden");
  sendBtn.disabled = true;
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    const data = await res.json();
    sessionId = data.session_id;
    localStorage.setItem("vega-session", sessionId);
    addMessage("assistant", data.reply);
    speak(data.reply);
  } catch {
    addMessage("assistant", "⚠️ I couldn't reach my own server. Is it still running?");
  } finally {
    typingEl.classList.add("hidden");
    sendBtn.disabled = false;
    input.focus();
  }
});

// ---------------------------------------------------------------------
// Jarvis v1 — voice out (speechSynthesis). Everything is wrapped so a
// TTS failure can never break the chat; typing always works alone.
// ---------------------------------------------------------------------

let voiceOn = localStorage.getItem("vega-voice") === "on";

function pickVoice() {
  try {
    if (!("speechSynthesis" in window)) return null;
    const voices = speechSynthesis.getVoices();
    return (
      voices.find((v) => /^en[-_]GB/i.test(v.lang) && /female/i.test(v.name)) ||
      voices.find((v) => /zira/i.test(v.name)) ||
      voices.find((v) => /^en/i.test(v.lang) && /female/i.test(v.name)) ||
      voices.find((v) => /^en/i.test(v.lang)) ||
      voices[0] ||
      null
    );
  } catch {
    return null;
  }
}

function speak(text) {
  if (!voiceOn) return;
  try {
    if (!("speechSynthesis" in window)) return;
    speechSynthesis.cancel(); // never talk over herself
    const clean = String(text)
      .replace(/\[DEMO MODE\]\s*/g, "")
      .replace(/[*_`#]/g, "");
    const utter = new SpeechSynthesisUtterance(clean);
    const voice = pickVoice();
    if (voice) utter.voice = voice;
    speechSynthesis.speak(utter);
  } catch {
    /* speech is a garnish — chat carries on without it */
  }
}

function stopSpeaking() {
  try {
    if ("speechSynthesis" in window) speechSynthesis.cancel();
  } catch {
    /* nothing to stop */
  }
}

function refreshVoiceUI() {
  voiceBtn.textContent = voiceOn ? "🔊 voice" : "🔇 voice";
  voiceBtn.classList.toggle("on", voiceOn);
  jarvisBadge.classList.toggle("hidden", !voiceOn);
}

voiceBtn.addEventListener("click", () => {
  if (!("speechSynthesis" in window)) {
    addMessage(
      "assistant",
      "This browser doesn't offer speech synthesis, so I can't talk " +
        "out loud here — Chrome or Edge can. Typing works fine."
    );
    return;
  }
  voiceOn = !voiceOn;
  localStorage.setItem("vega-voice", voiceOn ? "on" : "off");
  if (!voiceOn) stopSpeaking();
  refreshVoiceUI();
  if (voiceOn) speak("Voice on. I can talk now.");
});

if ("speechSynthesis" in window) {
  try {
    speechSynthesis.onvoiceschanged = () => pickVoice(); // warm the list
  } catch {
    /* voices may simply arrive late or never — pickVoice copes */
  }
}
refreshVoiceUI();

// ---------------------------------------------------------------------
// Jarvis v1 — voice in (Web Speech API). Chrome/Edge ship
// SpeechRecognition; where it's missing the mic button explains
// itself instead of failing silently.
// ---------------------------------------------------------------------

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let listening = false;

function stopListening() {
  listening = false;
  micBtn.classList.remove("listening");
  micBtn.textContent = "🎤";
}

if (SpeechRecognition) {
  try {
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.addEventListener("result", (event) => {
      const transcript = event.results[0][0].transcript.trim();
      if (transcript) {
        input.value = transcript;
        if (form.requestSubmit) form.requestSubmit();
        else form.dispatchEvent(new Event("submit", { cancelable: true }));
      }
    });
    recognition.addEventListener("end", stopListening);
    recognition.addEventListener("error", (event) => {
      stopListening();
      if (event.error === "not-allowed") {
        addMessage(
          "assistant",
          "The mic is blocked — allow microphone access for this page " +
            "and tap 🎤 again."
        );
      }
    });
  } catch {
    recognition = null;
  }
}

micBtn.addEventListener("click", () => {
  if (!recognition) {
    addMessage(
      "assistant",
      "Voice input needs a browser with speech recognition — Chrome " +
        "or Edge have it built in. This one doesn't, so typing it is."
    );
    return;
  }
  if (listening) {
    try {
      recognition.stop();
    } catch {
      stopListening();
    }
    return;
  }
  try {
    stopSpeaking(); // don't let her transcribe herself
    recognition.start();
    listening = true;
    micBtn.classList.add("listening");
    micBtn.textContent = "🔴";
  } catch {
    stopListening();
  }
});

resetBtn.addEventListener("click", async () => {
  stopSpeaking();
  if (sessionId) {
    try {
      await fetch("/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch { /* forgetting locally is enough */ }
  }
  sessionId = null;
  localStorage.removeItem("vega-session");
  messagesEl.innerHTML = "";
  addMessage("assistant", "Memory wiped. Fresh slate — who are you, and what are we doing?");
});

loadBadge();
addMessage("assistant", "VEGA online. Talk to me.");
