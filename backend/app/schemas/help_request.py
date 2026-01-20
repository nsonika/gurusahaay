"""
Help request schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class HelpRequestCreate(BaseModel):
    """
    Request body for creating a help request.
    Either query_text OR audio_base64 must be provided.
    """
    query_text: Optional[str] = None  # Text input
    audio_base64: Optional[str] = None  # Base64 encoded audio for voice input
    subject: Optional[str] = None
    grade: Optional[str] = None
    request_type: str = "text"  # text, voice, predefined


class HelpRequestResponse(BaseModel):
    id: UUID
    original_query_text: str
    detected_language: Optional[str]
    normalized_text: Optional[str]
    concept_id: Optional[str]
    subject: Optional[str]
    grade: Optional[str]
    request_type: str
    created_at: datetime

    class Config:
        from_attributes = True
