"""
Points and rewards tracking for gamification.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PointsHistory(Base):
    """
    Tracks points earned by teachers for various actions.
    
    Point values (suggested):
    - Upload content: +10
    - Content verified: +20
    - Content helped someone: +5
    - Gave feedback: +2
    """
    __tablename__ = "points_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    
    points = Column(Integer, nullable=False)
    reason = Column(Text)  # upload, verification, feedback, helped
    
    created_at = Column(DateTime, default=datetime.utcnow)
