"""
NeuraCRM FastAPI Application
Main application file with all routers and middleware configured
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

# Database and models
from api.db import engine
from api.models import Base

# Routers
from api.routers.auth import router as auth_router
from api.routers.kanban import router as kanban_router
from api.routers.conversational_ai import router as conversational_ai_router
from api.routers.rag import router as rag_router
# Add other routers as needed
from api.routers import users, payments, predictive_analytics, telephony, email_automation, chat, dashboard

# Services
from api.services.rag_service import rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting NeuraCRM application...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Initialize RAG service
    try:
        # Test RAG service initialization
        logger.info("Initializing RAG service...")
        # The service initializes itself when imported
        logger.info("RAG service initialized")
    except Exception as e:
        logger.warning(f"RAG service initialization failed: {e}")

    yield

    logger.info("Shutting down NeuraCRM application...")

# Create FastAPI application
app = FastAPI(
    title="NeuraCRM API",
    description="AI-powered Customer Relationship Management system with integrated call center capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred", "type": "database_error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred", "type": "internal_error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "NeuraCRM API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# API v1 prefix for all routes
api_prefix = "/api"

# Include routers
app.include_router(auth_router, prefix=api_prefix)
app.include_router(kanban_router, prefix=api_prefix)
app.include_router(conversational_ai_router, prefix=api_prefix)
app.include_router(rag_router, prefix=api_prefix)

# Additional routers (add as implemented)
try:
    app.include_router(users.router, prefix=api_prefix, tags=["users"])
except AttributeError:
    logger.warning("Users router not available")

try:
    app.include_router(payments.router, prefix=api_prefix, tags=["payments"])
except AttributeError:
    logger.warning("Payments router not available")

try:
    app.include_router(predictive_analytics.router, prefix=api_prefix, tags=["predictive-analytics"])
except AttributeError:
    logger.warning("Predictive analytics router not available")

try:
    app.include_router(telephony.router, prefix=api_prefix, tags=["telephony"])
except AttributeError:
    logger.warning("Telephony router not available")

try:
    app.include_router(email_automation.router, prefix=api_prefix, tags=["email-automation"])
except AttributeError:
    logger.warning("Email automation router not available")

try:
    app.include_router(chat.router, prefix=api_prefix, tags=["chat"])
except AttributeError:
    logger.warning("Chat router not available")

try:
    app.include_router(dashboard.router, prefix=api_prefix, tags=["dashboard"])
except AttributeError:
    logger.warning("Dashboard router not available")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to NeuraCRM API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "features": [
            "AI-powered lead scoring",
            "Sales forecasting with ensemble models",
            "Conversational AI with voice agents",
            "RAG-powered knowledge base Q&A",
            "Real-time call center integration",
            "Predictive customer analytics"
        ]
    }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "title": "NeuraCRM API",
        "version": "1.0.0",
        "description": "AI-powered CRM with integrated call center capabilities",
        "endpoints": {
            "authentication": "/api/auth",
            "leads & deals": "/api/kanban",
            "conversational AI": "/api/conversational-ai",
            "knowledge base": "/api/rag",
            "health check": "/health"
        },
        "ai_features": [
            "Lead scoring with multi-factor analysis",
            "Sales forecasting with ARIMA/Prophet/Linear Regression",
            "Sentiment analysis for customer interactions",
            "RAG-powered knowledge base Q&A",
            "Conversational AI with voice agents"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting NeuraCRM API server on port {port}...")
    uvicorn.run(
        "working_app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )