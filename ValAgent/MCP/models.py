from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: str
class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserData(BaseModel):
    user_id: int
    email: EmailStr
    name: str


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserData] = None

class SignupOut(BaseModel):
    ok: bool
    status_code: int
    message: str
    data: Optional[UserData]


class LoginOut(BaseModel):
    ok: bool
    status_code: int
    message: str
    data: Optional[TokenData]

class MeOut(BaseModel):
    ok: bool
    status_code: int
    message: str
    data: Optional[UserData]

# Users (for internal use later if needed)
class UserDTO(BaseModel):
    id: int
    email: EmailStr
    name: str

class RagAskInput(BaseModel):
    query: str
    top_k: int = 6

class EmailPayload(BaseModel):
    to: List[EmailStr]
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

class EnrollmentCreateIn(BaseModel):
    user_id: int
    course_id: int
    payment_id: int   # since payment-first flow


class EnrollmentCreateOut(BaseModel):
    enrollment_id: int
    status: Literal["PAID", "PENDING", "CANCELLED"]

class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    payment_id: int
    status: Literal["PAID", "PENDING", "CANCELLED"]

class DiscountOut(BaseModel):
    id: int
    code: str
    type: Literal["PERCENT", "AMOUNT"]
    value: float
    is_active: bool


class ListDiscountsOut(BaseModel):
    items: List[DiscountOut]

class DiscountApplyIn(BaseModel):
    course_id: int
    code: str

class DiscountApplyOut(BaseModel):
    course_id: int
    original_price_cents: int
    discount_id: Optional[int] = None
    discount_type: Optional[Literal["PERCENT","AMOUNT"]] = None
    discount_value: Optional[float] = None
    final_price_cents: int

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

class AuthValidateResponse(BaseModel):
    valid: bool
    sub: str
    iat: int
    exp: int
