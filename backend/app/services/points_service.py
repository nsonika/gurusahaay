"""
Points Service - Gamification and rewards tracking.

Point values:
- Upload content: +10
- Content verified: +20
- Content helped someone (worked=True): +5
- Gave feedback: +2
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.models.points import PointsHistory


class PointsService:
    """Handles points and rewards for teachers."""
    
    # Point values for different actions
    POINTS_UPLOAD = 10
    POINTS_VERIFIED = 20
    POINTS_HELPED = 5
    POINTS_FEEDBACK = 2
    
    @staticmethod
    def add_points(
        db: Session,
        teacher_id: UUID,
        points: int,
        reason: str
    ) -> PointsHistory:
        """Add points to a teacher's account."""
        entry = PointsHistory(
            teacher_id=teacher_id,
            points=points,
            reason=reason
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_total_points(db: Session, teacher_id: UUID) -> int:
        """Get total points for a teacher."""
        total = db.query(func.sum(PointsHistory.points)).filter(
            PointsHistory.teacher_id == teacher_id
        ).scalar()
        return total or 0
    
    @staticmethod
    def get_points_history(
        db: Session,
        teacher_id: UUID,
        limit: int = 50
    ) -> List[PointsHistory]:
        """Get points history for a teacher."""
        return db.query(PointsHistory).filter(
            PointsHistory.teacher_id == teacher_id
        ).order_by(
            PointsHistory.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def award_upload_points(db: Session, teacher_id: UUID) -> PointsHistory:
        """Award points for uploading content."""
        return PointsService.add_points(
            db, teacher_id, PointsService.POINTS_UPLOAD, "upload"
        )
    
    @staticmethod
    def award_verification_points(db: Session, teacher_id: UUID) -> PointsHistory:
        """Award points when content is verified."""
        return PointsService.add_points(
            db, teacher_id, PointsService.POINTS_VERIFIED, "verification"
        )
    
    @staticmethod
    def award_helped_points(db: Session, teacher_id: UUID) -> PointsHistory:
        """Award points when content helped someone."""
        return PointsService.add_points(
            db, teacher_id, PointsService.POINTS_HELPED, "helped"
        )
    
    @staticmethod
    def award_feedback_points(db: Session, teacher_id: UUID) -> PointsHistory:
        """Award points for giving feedback."""
        return PointsService.add_points(
            db, teacher_id, PointsService.POINTS_FEEDBACK, "feedback"
        )
