"""
Teacher schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class TeacherCreate(BaseModel):
    name: str
    phone: str
    password: str
    role: str = "teacher"
    language_preference: str = "en"
    school_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None


class TeacherResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    role: str
    language_preference: str
    school_name: Optional[str]
    district: Optional[str]
    state: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
