from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mail Service", version="1.0.0")


class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9+_.-]+@(.+)$", email))


@app.post("/api/email")
def send_email(request: EmailSendRequest):
    if not request.to or not request.subject or not request.body:
        return {"status": "error", "message": "Invalid email request: missing required fields"}

    if not is_valid_email(request.to):
        return {"status": "error", "message": "Invalid email address"}

    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")

    msg = MIMEText(request.body)
    msg["From"] = username
    msg["To"] = request.to
    msg["Subject"] = request.subject

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, request.to, msg.as_string())

        logger.info(f"Email sent to {request.to} with subject '{request.subject}'")
        return {"status": "success", "message": "Email sent successfully"}

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {"status": "error", "message": f"Failed to send email: {str(e)}"}
