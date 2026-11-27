// MAMAR chat page — plain JS, no build step.
"use strict";

const messagesEl = document.getElementById("messages");
const typingEl = document.getElementById("typing");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = form.querySelector("button");
const badge = document.getElementById("mode-badge");
const resetBtn = document.getElementById("reset-btn");

let sessionId = localStorage.getItem("mamar-session") || null;

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
    localStorage.setItem("mamar-session", sessionId);
    addMessage("assistant", data.reply);
  } catch {
    addMessage("assistant", "⚠️ I couldn't reach my own server. Is it still running?");
  } finally {
    typingEl.classList.add("hidden");
    sendBtn.disabled = false;
    input.focus();
  }
});

resetBtn.addEventListener("click", async () => {
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
  localStorage.removeItem("mamar-session");
  messagesEl.innerHTML = "";
  addMessage("assistant", "Memory wiped. Fresh slate — who are you, and what are we doing?");
});

loadBadge();
addMessage("assistant", "MAMAR online. Talk to me.");
