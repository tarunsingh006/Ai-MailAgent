const API = "http://localhost:8001";
let sessionId = crypto.randomUUID();

const messagesEl = document.getElementById("messages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const mailHistory = document.getElementById("mailHistory");

// Auto-resize textarea
userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 160) + "px";
});

// Send on Enter (Shift+Enter for newline)
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);
document.getElementById("newChatBtn").addEventListener("click", newChat);

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Remove welcome screen
    const welcome = messagesEl.querySelector(".welcome");
    if (welcome) welcome.remove();

    appendMessage("user", text);
    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.disabled = true;

    const typingEl = appendTyping();

    try {
        const res = await fetch(`${API}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message: text }),
        });

        const data = await res.json();
        typingEl.remove();

        appendMessage("agent", data.reply, data.action === "sent");

        if (data.action === "sent") {
            loadHistory();
        }
    } catch {
        typingEl.remove();
        appendMessage("agent", "❌ Could not reach the agent. Make sure it's running on localhost:8000.");
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function appendMessage(role, text, sent = false) {
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "U" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = formatText(text);

    if (sent) {
        const badge = document.createElement("div");
        badge.className = "sent-badge";
        badge.textContent = "✅ Email Sent";
        bubble.appendChild(badge);
    }

    div.appendChild(avatar);
    div.appendChild(bubble);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
}

function appendTyping() {
    const div = document.createElement("div");
    div.className = "message agent typing";
    div.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="bubble">Thinking...</div>
    `;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
}

function formatText(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");
}

async function loadHistory() {
    try {
        const res = await fetch(`${API}/history`);
        const data = await res.json();

        if (!data.emails.length) return;

        mailHistory.innerHTML = "";
        data.emails.forEach(mail => {
            const item = document.createElement("div");
            item.className = "mail-item";
            item.innerHTML = `
                <div class="mail-to">To: ${mail.to}</div>
                <div class="mail-subject">${mail.subject}</div>
            `;
            mailHistory.appendChild(item);
        });
    } catch {
        // silently fail
    }
}

async function newChat() {
    // Reset session on backend
    await fetch(`${API}/reset?session_id=${sessionId}`, { method: "POST" }).catch(() => {});
    sessionId = crypto.randomUUID();
    messagesEl.innerHTML = `
        <div class="welcome">
            <h2>👋 Hi, I'm your Mail Agent</h2>
            <p>Tell me who you want to email and what about — I'll draft it for you.</p>
        </div>
    `;
}

// Load history on startup
loadHistory();
