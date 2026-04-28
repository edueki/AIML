from server import mcp
from server import http_post
from config import PAYMENT_URL
from models import PaymentIntentIn,PaymentIntentOut
from typing import Optional

@mcp.tool(
    name="create_payment_intent",
    description="Create a payment for a course and must be done for any course enrollment."
)
async def create_payment_intent(
    payment_input: PaymentIntentIn
) -> PaymentIntentOut:
    """
    Calls POST /payments with:
    {
        "user_id": int,
        "course_id": int,
        "amount_cents": int
    }
    """

    url = PAYMENT_URL.rstrip("/")

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    resp = await http_post(
        url,
        headers=headers,
        body=payment_input.model_dump(),
    )

    return PaymentIntentOut(**resp)