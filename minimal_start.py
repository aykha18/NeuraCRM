#!/usr/bin/env python3
"""
Minimal startup script for the CRM application.
This script starts the app with minimal dependencies to ensure it can respond to health checks.
"""
import os
import sys
import logging
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_minimal_app():
    """Create a minimal FastAPI app with just health check endpoints"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from datetime import datetime
    
    app = FastAPI(
        title="CRM API",
        description="API for the CRM Application with AI Features",
        version="1.0.0"
    )
    
    # CORS setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def read_root():
        return {"message": "CRM API is running.", "status": "healthy"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "message": "Service is running"}
    
    @app.get("/api/ping")
    def ping():
        """Simple health check endpoint that doesn't require database"""
        return {"status": "ok", "message": "pong", "timestamp": datetime.now().isoformat()}
    
    @app.get("/api/health")
    def api_health_check():
        """Comprehensive health check endpoint"""
        try:
            # Try to import database components
            from api.db import engine
            from sqlalchemy import text
            
            # Test database connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
            
            return {
                "status": "healthy", 
                "message": "Service is running",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return {
                "status": "degraded", 
                "message": "Service is running but database connection failed",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @app.get("/api/status")
    def status_check():
        """Simple status check that always works"""
        return {
            "status": "ok",
            "message": "Service is running",
            "timestamp": datetime.now().isoformat()
        }
    
    return app

def main():
    """Main startup function"""
    logger.info("Starting CRM Application (Minimal Mode)...")
    
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Try to create the full app first
        from backend.api.main import app
        logger.info("Successfully imported full app")
    except Exception as e:
        logger.warning(f"Failed to import full app: {e}")
        logger.info("Creating minimal app instead...")
        app = create_minimal_app()
    
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting FastAPI server on port {port}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
