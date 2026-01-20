"""
HelpRequest model - tracks teacher queries for analytics and improvement.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class HelpRequest(Base):
    """
    Stores every help request from teachers.
    Used for:
    - Analytics on common problems
    - Improving concept synonym coverage
    - Tracking unresolved queries for content gaps
    """
    __tablename__ = "help_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    
    # Original input
    original_query_text = Column(Text, nullable=False)
    detected_language = Column(Text)  # en, kn, hi
    
    # Processed input
    normalized_text = Column(Text)  # After suffix stripping
    concept_id = Column(Text, ForeignKey("concepts.concept_id"))  # Resolved concept
    
    # Context
    subject = Column(Text)
    grade = Column(Text)
    request_type = Column(Text)  # text, voice, predefined
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = relationship("HelpResponse", back_populates="help_request")


class HelpResponse(Base):
    """
    Responses to help requests from other teachers.
    """
    __tablename__ = "help_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    help_request_id = Column(UUID(as_uuid=True), ForeignKey("help_requests.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    
    response_text = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    help_request = relationship("HelpRequest", back_populates="responses")
