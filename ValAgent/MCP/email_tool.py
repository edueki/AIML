from server import mcp
from server import http_post
from config import EMAIL_URL
from models import EmailPayload
from typing import Dict,Any

@mcp.tool(
    name="send_email",
    description="Send an email using the EDUeki email service. Supports HTML, text, CC, and BCC."
)
async def send_email(payload: EmailPayload) -> Dict[str, Any]:
    """
    Calls POST /email/send with:
    {
        "to": [...],
        "subject": "...",
        "body_html": "...",
        "body_text": "...",
        "cc": [...],
        "bcc": [...]
    }
    """
    url = f"{EMAIL_URL.rstrip('/')}/email/send"

    return await http_post(
        url,    # payload already matches expected schema
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        body=payload.model_dump(),
    )