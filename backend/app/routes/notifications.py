"""
Notification routes - handles notification retrieval and management.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from app.database import get_db
from app.models.teacher import Teacher
from app.models.notification import Notification
from app.routes.auth import get_current_teacher

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationOut(BaseModel):
    id: str
    notification_type: str
    title: str
    message: str
    reference_id: str | None
    reference_type: str | None
    is_read: bool
    created_at: str


class NotificationCountOut(BaseModel):
    unread_count: int


@router.get("", response_model=List[NotificationOut])
def get_notifications(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get notifications for the current teacher.
    """
    notifications = db.query(Notification).filter(
        Notification.teacher_id == current_teacher.id
    ).order_by(
        desc(Notification.created_at)
    ).limit(limit).all()
    
    return [
        NotificationOut(
            id=str(n.id),
            notification_type=n.notification_type,
            title=n.title,
            message=n.message,
            reference_id=n.reference_id,
            reference_type=n.reference_type,
            is_read=n.is_read,
            created_at=n.created_at.isoformat()
        )
        for n in notifications
    ]


@router.get("/unread-count", response_model=NotificationCountOut)
def get_unread_count(
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get count of unread notifications.
    """
    count = db.query(Notification).filter(
        Notification.teacher_id == current_teacher.id,
        Notification.is_read == False
    ).count()
    
    return NotificationCountOut(unread_count=count)


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Mark a notification as read.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.teacher_id == current_teacher.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {"status": "ok"}


@router.post("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Mark all notifications as read.
    """
    db.query(Notification).filter(
        Notification.teacher_id == current_teacher.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return {"status": "ok"}


# Helper function to create notifications
def create_notification(
    db: Session,
    teacher_id: UUID,
    notification_type: str,
    title: str,
    message: str,
    reference_id: str = None,
    reference_type: str = None
):
    """
    Create a new notification for a teacher.
    """
    notification = Notification(
        teacher_id=teacher_id,
        notification_type=notification_type,
        title=title,
        message=message,
        reference_id=reference_id,
        reference_type=reference_type
    )
    db.add(notification)
    db.commit()
    return notification
