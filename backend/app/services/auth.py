"""
Authentication service - JWT token management and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from uuid import UUID

from app.config import get_settings
from app.models.teacher import Teacher
from app.schemas.auth import TokenData

settings = get_settings()


class AuthService:
    """Handles authentication operations."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def create_access_token(teacher_id: UUID) -> str:
        """
        Create a JWT access token for a teacher.
        Token contains teacher_id and expiration time.
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode = {
            "sub": str(teacher_id),
            "exp": expire
        }
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        Returns TokenData if valid, None if invalid.
        """
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            teacher_id: str = payload.get("sub")
            if teacher_id is None:
                return None
            return TokenData(teacher_id=teacher_id)
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_teacher(db: Session, phone: str, password: str) -> Optional[Teacher]:
        """
        Authenticate a teacher by phone and password.
        Returns Teacher if valid, None if invalid.
        """
        teacher = db.query(Teacher).filter(Teacher.phone == phone).first()
        if not teacher:
            return None
        if not AuthService.verify_password(password, teacher.password_hash):
            return None
        return teacher
    
    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: UUID) -> Optional[Teacher]:
        """Get a teacher by their ID."""
        return db.query(Teacher).filter(Teacher.id == teacher_id).first()
