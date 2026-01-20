"""
Points schemas.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class PointsHistoryItem(BaseModel):
    id: UUID
    points: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PointsResponse(BaseModel):
    total_points: int
    history: List[PointsHistoryItem]
