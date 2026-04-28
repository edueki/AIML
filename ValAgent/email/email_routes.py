import os
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter(prefix="/email", tags=["email"])

conf = ConnectionConfig(

    MAIL_FROM=os.getenv("MAIL_FROM","eduekilearning@gmail.com"),
    MAIL_USERNAME= os.getenv("MAIL_USERNAME", "eduekilearning@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", " "),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME","EDUeki Learning"),
    MAIL_PORT=os.getenv("MAIL_PORT",587),
    MAIL_SERVER=os.getenv("MAIL_SERVER","smtp.gmail.com"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=os.getenv("MAIL_USE_CREDENTIALS", "True").lower() == "true",
    VALIDATE_CERTS=os.getenv("MAIL_VALIDATE_CERTS", "True").lower() == "true",
)

class EmailPayload(BaseModel):
    to: List[EmailStr]
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

@router.post("/send")
async def send_email(payload: EmailPayload, background_tasks: BackgroundTasks):
    subtype = MessageType.html if payload.body_html else MessageType.plain
    body = payload.body_html or payload.body_text or ""
    message = MessageSchema(
        subject=payload.subject,
        recipients=payload.to,
        cc=payload.cc or [],
        bcc=payload.bcc or [],
        body=body,
        subtype=subtype,
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"ok": True}

@router.post("/send-with-attachments")
async def send_with_attachments(
    background_tasks: BackgroundTasks,
    to: List[EmailStr] = Form(...),
    subject: str = Form(...),
    body_html: Optional[str] = Form(None),
    body_text: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
        raise HTTPException(status_code=500, detail=f"Failed to queue email: {str(e)}")
