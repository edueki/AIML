# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class CourseOut(BaseModel):
    id: int
    title: str
    slug: str
    short_desc: str
    long_desc: Optional[str] = None
    price_cents: int
    is_active: bool

class CourseListOut(BaseModel):
    items: List[CourseOut]
    total: int
    
class CourseCreateIn(BaseModel):
    title: str
    slug: str
    short_desc: str
    long_desc: Optional[str] = None
    price_cents: int
    is_active: bool = True

class CourseCreateOut(BaseModel):
    id: int
    title: str

