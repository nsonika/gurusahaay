"""
Authentication schemas.
"""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    phone: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    teacher_id: Optional[str] = None
