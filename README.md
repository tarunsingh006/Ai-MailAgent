# Personal Mail Agent

**An AI-powered email automation system using Google Gemini and Python FastAPI**

A microservices application built entirely in Python. Users send a natural language prompt describing what they want to email about, and the Gemini AI composes a professional email and sends it via Gmail SMTP.

**Author**: [tarunsingh](https://github.com/tarunsingh006)  
**Version**: 3.0.0

> **v3.0.0** — Migrated the mail service from Java Spring Boot to Python FastAPI for a 100% Python stack.

---

## 📊 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Agent Service                      │
│              (Python 3.10+ / Gemini 2.5-Flash)              │
│         • AI Email Composition  • Word Count Control         │
│                    Port 8000                                 │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP POST (JSON)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Mail Service                            │
│                 (Python 3.10+ / smtplib)                    │
│         • SMTP Gateway  • Email Delivery                     │
│                    Port 8080                                 │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
              Gmail SMTP Server
```

## ✨ Features

- **🤖 AI Email Writing** — Gemini 2.5-Flash composes professional emails from a simple prompt
- **📏 Word Count Control** — Specify a minimum word count; the agent regenerates if too short
- **📧 Gmail SMTP Delivery** — Emails sent via Python smtplib through Gmail
- **⚡ Async Architecture** — Non-blocking HTTP calls between services using `httpx`
- **🐍 100% Python** — Both services built with FastAPI, no Java required
- **📚 Swagger Docs** — Interactive API docs at `/docs` for both services

## 📋 Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Runtime for both services |
| **Docker** | 20.10+ | Container deployment (optional) |
| **Gmail Account** | — | SMTP email delivery |
| **Gemini API Key** | — | Google AI for email composition |

## 🛠️ Setup

### 1. Get Credentials

- **Gmail App Password**: Enable 2FA → [Generate App Password](https://myaccount.google.com/apppasswords)
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/apikey)

### 2. Configure Environment

**EmailAgent/.env:**
```
GOOGLE_API_KEY=your_gemini_api_key
MAIL_SERVICE_URL=http://localhost:8080
```

**mail-service-python/.env:**
```
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_specific_password
```

### 3. Start Services

**Terminal 1 — Python Mail Service:**
```bash
cd mail-service-python
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
# Running on http://localhost:8080
```

**Terminal 2 — Python AI Agent:**
```bash
cd EmailAgent
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
uvicorn main:app --reload
# Running on http://localhost:8000
```

## 📁 Project Structure

```
PersonalMailAgent/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── EmailAgent/                          # Python FastAPI AI Agent
│   ├── main.py                         # AI logic & entry point
│   ├── requirements.txt
│   └── .env                            # GOOGLE_API_KEY (not committed)
│
├── mail-service-python/                 # Python FastAPI Mail Service
│   ├── main.py                         # SMTP gateway
│   ├── requirements.txt
│   └── .env                            # MAIL_USERNAME, MAIL_PASSWORD (not committed)
│
└── mail-tool-service/                   # Legacy Java Spring Boot (replaced in v3.0.0)
```

## 🔌 API Reference

### POST `/chat` — Compose & Send Email

Send a prompt and the agent writes a professional email and delivers it.

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "email": "recipient@example.com",
    "content": "Thank them for attending the meeting and confirm next steps",
    "words": 200
  }'
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `email` | string | *required* | Recipient email address |
| `content` | string | *required* | What the email should be about |
| `words` | int | `150` | Minimum word count |

**Response:**
```json
{
  "status": "Email Sent",
  "service_response": {
    "success": true,
    "data": "Email sent successfully"
  }
}
```

### POST `/api/email` — Direct Email (Mail Service)

Send an email directly without AI composition.

```bash
curl -X POST http://localhost:8080/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Meeting Confirmation",
    "body": "Hi, confirming our meeting tomorrow at 2pm."
  }'
```

### Interactive Documentation

| Service | URL |
|---------|-----|
| AI Agent Swagger | http://localhost:8000/docs |
| Mail Service Swagger | http://localhost:8080/docs |

## ⚙️ Environment Variables

| Variable | Service | Required | Description |
|----------|---------|----------|-------------|
| `GOOGLE_API_KEY` | EmailAgent | ✅ | Gemini API key |
| `MAIL_USERNAME` | mail-service-python | ✅ | Gmail address |
| `MAIL_PASSWORD` | mail-service-python | ✅ | Gmail app-specific password |
| `MAIL_SERVICE_URL` | EmailAgent | ❌ | Mail service URL (default: `http://localhost:8080`) |

## 🧰 Tech Stack

### AI Agent (EmailAgent)
| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.135.1 | Web framework |
| Uvicorn | 0.41.0 | ASGI server |
| LangChain Core | 1.2.16 | LLM abstraction |
| LangChain Google GenAI | 4.2.1 | Gemini integration |
| Pydantic | 2.12.5 | Request validation |
| httpx | 0.28.1 | Async HTTP client |
| python-dotenv | 1.2.2 | Environment variables |

### Mail Service (mail-service-python)
| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115.0 | Web framework |
| Uvicorn | 0.30.0 | ASGI server |
| smtplib | built-in | Gmail SMTP sending |
| python-dotenv | 1.0.1 | Environment variables |

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| `GOOGLE_API_KEY` missing | Create `.env` in `EmailAgent/` with your Gemini API key |
| SMTP authentication failed | Use a Gmail [App Password](https://myaccount.google.com/apppasswords), not your regular password |
| Connection refused to mail service | Start `mail-service-python` on port 8080 first |
| Module not found errors | Activate the virtual environment and run `pip install -r requirements.txt` |
| `(.venv)` not showing | Run `.venv\Scripts\activate` before installing packages |

---

**Made with ❤️ by tarunsingh**
