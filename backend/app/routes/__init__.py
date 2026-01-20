"""
API Routes - FastAPI routers for all endpoints.
"""
from app.routes.auth import router as auth_router
from app.routes.concepts import router as concepts_router
from app.routes.help import router as help_router
from app.routes.suggestions import router as suggestions_router
from app.routes.content import router as content_router
from app.routes.community import router as community_router
from app.routes.points import router as points_router
from app.routes.translate import router as translate_router
from app.routes.notifications import router as notifications_router
from app.routes.ai import router as ai_router

__all__ = [
    "auth_router",
    "concepts_router",
    "help_router",
    "suggestions_router",
    "content_router",
    "community_router",
    "points_router",
    "translate_router",
    "notifications_router",
    "ai_router",
]
