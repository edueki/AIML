from pydantic import BaseModel, EmailStr, Field
from typing import Optional

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
