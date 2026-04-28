# payments/schemas.py
from pydantic import BaseModel
from typing import Literal, Optional

class PaymentIntentIn(BaseModel):
    user_id: int
    course_id: int
    amount_cents: int


class PaymentIntentOut(BaseModel):
    payment_id: int
    user_id: int
    course_id: int
    provider: Literal["MOCK"]
    provider_ref: str
    amount_cents: int
    currency: str
    status: Literal["PAID", "PENDING", "FAILED"]

