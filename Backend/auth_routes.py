import os
import smtplib
import hashlib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from secrets import randbelow

import firebase_admin
from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException
from firebase_admin import auth, credentials
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

# Initialize Firebase Admin once
service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "firebase-service-account.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

# Temporary in-memory OTP storage for demo/class project
otp_store = {}


class OTPVerifyRequest(BaseModel):
    code: str


def send_email_otp(to_email: str, code: str) -> None:
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_APP_PASSWORD")

    if not sender or not password:
        raise Exception("SMTP credentials are missing in Backend/.env")

    subject = "Your NutritionApp 2FA Code"
    body = (
        f"Your verification code is: {code}\n\n"
        "This code will expire in 5 minutes."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


def verify_firebase_token(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    token = authorization.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")


@router.post("/auth/send-otp")
def send_otp(authorization: str = Header(None)):
    decoded = verify_firebase_token(authorization)
    email = decoded.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="User email not found")

    code = f"{randbelow(900000) + 100000}"
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    otp_store[email] = {
        "code_hash": code_hash,
        "expires_at": expires_at,
        "verified": False,
        "attempts": 0,
    }

    try:
        send_email_otp(email, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {str(e)}")

    return {"message": "OTP sent successfully"}


@router.post("/auth/verify-otp")
def verify_otp(payload: OTPVerifyRequest, authorization: str = Header(None)):
    decoded = verify_firebase_token(authorization)
    email = decoded.get("email")

    if not email or email not in otp_store:
        raise HTTPException(status_code=400, detail="No OTP request found")

    record = otp_store[email]

    if datetime.now(timezone.utc) > record["expires_at"]:
        del otp_store[email]
        raise HTTPException(status_code=400, detail="OTP expired")

    if record["attempts"] >= 5:
        del otp_store[email]
        raise HTTPException(status_code=429, detail="Too many attempts")

    submitted_hash = hashlib.sha256(payload.code.encode()).hexdigest()

    if submitted_hash != record["code_hash"]:
        record["attempts"] += 1
        raise HTTPException(status_code=400, detail="Invalid OTP")

    record["verified"] = True

    return {
        "message": "2FA verified successfully",
        "email": email,
    }