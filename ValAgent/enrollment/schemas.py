from pydantic import BaseModel
from typing import Literal, Optional


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
