"""
Points and rewards routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.teacher import Teacher
from app.schemas.points import PointsResponse, PointsHistoryItem
from app.routes.auth import get_current_teacher
from app.services.points_service import PointsService

router = APIRouter(prefix="/points", tags=["Points"])


@router.get("", response_model=PointsResponse)
def get_points(
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get current teacher's points and history.
    """
    total = PointsService.get_total_points(db, current_teacher.id)
    history = PointsService.get_points_history(db, current_teacher.id)
    
    return PointsResponse(
        total_points=total,
        history=[
            PointsHistoryItem(
                id=h.id,
                points=h.points,
                reason=h.reason,
                created_at=h.created_at
            )
            for h in history
        ]
    )
