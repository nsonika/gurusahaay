"""
Teacher model - represents educators using the platform.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    phone = Column(Text, unique=True, nullable=False)  # Used for login
    password_hash = Column(Text, nullable=False)  # Hashed password
    role = Column(Text, default="teacher")  # teacher, mentor, admin
    language_preference = Column(Text, default="en")  # en, kn, hi
    school_name = Column(Text)
    district = Column(Text)
    state = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
