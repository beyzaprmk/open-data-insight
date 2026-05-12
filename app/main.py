import os
from contextlib import contextmanager
from typing import Generator

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.models import Base
from app.api.routes import health, data_files, datasets
from app.services.data_file_service import DataFileService


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:adminpassword@localhost:5432/opendata_db"
)

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Used by route handlers to get DB access.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create FastAPI app
app = FastAPI(
    title="OpenDataInsight API",
    description="API for managing datasets, images, and analysis with Cloudinary integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()
    print("Database initialized successfully")


# Health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "service": "OpenDataInsight API",
        "version": "1.0.0"
    }


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(datasets.router, tags=["datasets"])
app.include_router(data_files.router, tags=["data-files"])


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "OpenDataInsight API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return {
        "status": "error",
        "detail": str(exc)
    }


@app.exception_handler(PermissionError)
async def permission_error_handler(request, exc):
    """Handle PermissionError exceptions."""
    return {
        "status": "error",
        "detail": str(exc),
        "status_code": 403
    }


# Application context manager for testing
@contextmanager
def get_app_context():
    """Context manager for application initialization."""
    db = SessionLocal()
    try:
        yield app, db
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m uvicorn app.main:app --reload
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info")
    )
