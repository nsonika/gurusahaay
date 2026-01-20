"""
SQLAlchemy models - mirrors the database schema exactly.
All models use UUID primary keys for security and scalability.
"""
from app.models.teacher import Teacher
from app.models.concept import Concept, ConceptSynonym
from app.models.help_request import HelpRequest, HelpResponse
from app.models.content import UploadedContent, ContentFeedback, ContentInteraction
from app.models.points import PointsHistory
from app.models.notification import Notification

__all__ = [
    "Teacher",
    "Concept",
    "ConceptSynonym",
    "HelpRequest",
    "HelpResponse",
    "UploadedContent",
    "ContentFeedback",
    "ContentInteraction",
    "PointsHistory",
    "Notification",
]
