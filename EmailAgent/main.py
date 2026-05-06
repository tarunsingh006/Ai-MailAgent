from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
from dotenv import load_dotenv
load_dotenv()
import httpx
import logging
import json
from typing import Optional, Dict, Any
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal Mail Agent", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.8,
    max_output_tokens=2048,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

logger.info("Gemini initialized")

# In-memory session store: session_id -> list of messages
sessions: Dict[str, list] = {}

# Last 5 sent emails
sent_emails: deque = deque(maxlen=5)

SYSTEM_PROMPT = """You are a friendly personal email assistant. Your job is to help the user draft and send emails through natural conversation.

Your behavior:
- Greet the user warmly on first message
- Gather information naturally through conversation: recipient email, what the email is about, and preferred length (optional, default 150 words)
- Once you have enough info, draft a professional email and present it clearly
- After showing the draft, ask if they want to send it, modify it, or start over
- If user wants changes, redraft accordingly
- When user confirms to send, respond with a JSON block ONLY in this exact format (nothing else on that line):
  SEND_EMAIL:{"to":"email","subject":"subject","body":"full email body"}
- Keep responses concise and conversational
- The sender's name is Bharat, emails should be signed "Warm regards, Bharat"
"""


class ChatMessage(BaseModel):
    session_id: str = Field(default="default")
    message: str


class ChatReply(BaseModel):
    reply: str
    action: Optional[str] = None  # "sent", "draft_ready"
    sent_email: Optional[Dict[str, Any]] = None


class SendRequest(BaseModel):
    email: str
    subject: str
    body: str


def extract_text(resp):
    content = resp.content
    if isinstance(content, list):
        return " ".join(part.get("text", "") for part in content)
    return content


async def call_email_service(to: str, subject: str, body: str):
    mail_service_url = os.getenv("MAIL_SERVICE_URL", "http://localhost:8001")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{mail_service_url}/api/email",
                json={"to": to, "subject": subject, "body": body}
            )
            response.raise_for_status()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


@app.post("/chat", response_model=ChatReply)
async def chat(msg: ChatMessage):
    session_id = msg.session_id

    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    # Build messages for LLM
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in history:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=msg.message))

    response = llm.invoke(messages)
    reply_text = extract_text(response)

    # Save to history
    history.append({"role": "user", "content": msg.message})
    history.append({"role": "assistant", "content": reply_text})

    # Check if agent wants to send email
    if "SEND_EMAIL:" in reply_text:
        try:
            json_str = reply_text.split("SEND_EMAIL:")[1].split("\n")[0].strip()
            email_data = json.loads(json_str)

            result = await call_email_service(
                to=email_data["to"],
                subject=email_data["subject"],
                body=email_data["body"]
            )

            if result["success"]:
                sent_emails.appendleft({
                    "to": email_data["to"],
                    "subject": email_data["subject"],
                    "preview": email_data["body"][:120] + "..."
                })
                # Clean reply for display
                clean_reply = reply_text.replace(f"SEND_EMAIL:{json_str}", "").strip()
                if not clean_reply:
                    clean_reply = f"✅ Email sent to **{email_data['to']}** successfully!"

                history[-1]["content"] = clean_reply
                return ChatReply(reply=clean_reply, action="sent", sent_email=email_data)
            else:
                return ChatReply(reply=f"❌ Failed to send: {result.get('error')}")
        except Exception as e:
            logger.error(f"Send parse error: {e}")

    return ChatReply(reply=reply_text)


@app.get("/history")
def get_history():
    return {"emails": list(sent_emails)}


@app.post("/reset")
def reset_session(session_id: str = "default"):
    sessions.pop(session_id, None)
    return {"status": "reset"}
