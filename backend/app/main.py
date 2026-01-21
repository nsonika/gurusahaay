"""
GuruSahaay Backend - FastAPI Application

A mobile-first web application providing just-in-time classroom support for teachers.
Supports Kannada, Hindi, and English with concept-based multilingual search.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import (
    auth_router,
    concepts_router,
    help_router,
    suggestions_router,
    content_router,
    community_router,
    points_router,
    translate_router,
    notifications_router,
    ai_router,
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="GuruSahaay API",
    description="Just-in-time classroom support for teachers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(concepts_router)
app.include_router(help_router)
app.include_router(suggestions_router)
app.include_router(content_router)
app.include_router(community_router)
app.include_router(points_router)
app.include_router(translate_router)
app.include_router(notifications_router)
app.include_router(ai_router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "GuruSahaay",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "whisper": "available"
    }
