from pydantic import BaseModel
from typing import Optional, Literal, List

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

# Optional helpers for seeding/listing during tests
class DiscountSeedIn(BaseModel):
    code: str
    type: Literal["PERCENT","AMOUNT"]
    value: float
    is_active: bool = True

class DiscountOut(BaseModel):
    id: int
    code: str
    type: Literal["PERCENT","AMOUNT"]
    value: float
    is_active: bool
