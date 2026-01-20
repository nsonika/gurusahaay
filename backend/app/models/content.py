"""
Content models - uploaded teaching resources and feedback.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class UploadedContent(Base):
    """
    Teaching content uploaded by teachers or ingested from external sources.
    
    source_type values:
    - 'internal': Uploaded by a teacher
    - 'external': Fetched from YouTube/blogs (requires verification)
    
    is_verified:
    - True: Reviewed and approved by mentor/admin
    - False: Pending review (external content starts here)
    """
    __tablename__ = "uploaded_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("teachers.id"))
    
    # Concept linkage - CRITICAL for search
    concept_id = Column(Text, ForeignKey("concepts.concept_id"), nullable=False)
    subject = Column(Text)
    grade = Column(Text)
    language = Column(Text, nullable=False)  # en, kn, hi
    
    # Content details
    content_type = Column(Text)  # video, document, activity, tip
    title = Column(Text, nullable=False)
    content_url = Column(Text)  # URL or file path
    description = Column(Text)  # Brief summary
    
    # Source tracking
    source_type = Column(Text, default="internal")  # internal, external
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentFeedback(Base):
    """
    Teacher feedback on content - used for ranking and quality control.
    """
    __tablename__ = "content_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_content.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    
    worked = Column(Boolean)  # Did this help solve the problem?
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentInteraction(Base):
    """
    Tracks content views/clicks for analytics and ranking.
    """
    __tablename__ = "content_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_content.id"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    
    interaction_type = Column(Text)  # view, click, share, save
    
    created_at = Column(DateTime, default=datetime.utcnow)
