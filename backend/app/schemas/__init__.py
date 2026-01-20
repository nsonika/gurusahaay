"""
Pydantic schemas for request/response validation.
"""
from app.schemas.auth import LoginRequest, LoginResponse, TokenData
from app.schemas.teacher import TeacherResponse, TeacherCreate
from app.schemas.concept import ConceptResponse, ConceptSynonymResponse
from app.schemas.help_request import HelpRequestCreate, HelpRequestResponse
from app.schemas.content import (
    ContentUploadRequest,
    ContentResponse,
    ContentFeedbackRequest,
    SuggestionResponse,
)
from app.schemas.points import PointsResponse, PointsHistoryItem

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "TokenData",
    "TeacherResponse",
    "TeacherCreate",
    "ConceptResponse",
    "ConceptSynonymResponse",
    "HelpRequestCreate",
    "HelpRequestResponse",
    "ContentUploadRequest",
    "ContentResponse",
    "ContentFeedbackRequest",
    "SuggestionResponse",
    "PointsResponse",
    "PointsHistoryItem",
]
