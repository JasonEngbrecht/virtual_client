"""
Virtual Client - Social Work Training Application
Main FastAPI application entry point
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import all models to ensure they're registered with SQLAlchemy
# This must happen before any database operations
from .models import (
    ClientProfileDB,
    EvaluationRubricDB,
    SessionDB,
    EvaluationDB,
    CourseSectionDB,
    SectionEnrollmentDB,
    AssignmentDB,
    AssignmentClientDB
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # Startup
    logger.info("Starting Virtual Client application...")
    # TODO: Initialize database connection
    # TODO: Load configuration
    yield
    # Shutdown
    logger.info("Shutting down Virtual Client application...")
    # TODO: Close database connections
    # TODO: Cleanup resources


# Create FastAPI application instance
app = FastAPI(
    title="Virtual Client - Social Work Training",
    description="AI-powered virtual clients for social work education",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Virtual Client API is running",
        "version": "0.1.0",
        "status": "healthy"
    }


# API health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "virtual-client-api"
    }


# TODO: Import and include routers
from .api import teacher_routes, student_routes

# Include routers
app.include_router(teacher_routes.router, prefix="/api")
app.include_router(student_routes.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
