"""
Notification model - stores notifications for teachers.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Notification(Base):
    """
    Stores notifications for teachers.
    Types:
    - help_response: Someone responded to your help request
    - content_upload: Someone uploaded content for a topic you asked about
    - points_earned: You earned points
    - leaderboard: Leaderboard update
    """
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    
    notification_type = Column(Text, nullable=False)  # help_response, content_upload, points_earned, leaderboard
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    
    # Optional reference to related entity
    reference_id = Column(Text)  # ID of help request, content, etc.
    reference_type = Column(Text)  # help_request, content, points
    
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
