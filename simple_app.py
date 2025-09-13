#!/usr/bin/env python3
"""
Simple CRM App - Serves both API and Frontend
No complex imports, just works.
"""
import os
import sys
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CRM API",
    description="API for the CRM Application",
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

# Check if frontend files exist
frontend_path = os.path.join(os.getcwd(), "frontend_dist")
logger.info(f"Looking for frontend at: {frontend_path}")
logger.info(f"Frontend exists: {os.path.exists(frontend_path)}")

if os.path.exists(frontend_path):
    logger.info("Mounting frontend static files")
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    # Serve frontend at root
    @app.get("/")
    def serve_frontend():
        """Serve the React frontend"""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"error": "Frontend not found"}
    
    # Catch-all for frontend routes
    @app.get("/{path:path}")
    def serve_frontend_routes(path: str):
        """Serve frontend for all non-API routes"""
        # Don't serve API routes
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve static files if they exist
        static_file_path = os.path.join(frontend_path, path)
        if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
            return FileResponse(static_file_path)
        
        # Serve index.html for React Router
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
else:
    logger.warning("Frontend not found, serving API only")
    
    @app.get("/")
    def read_root():
        return {"message": "CRM API is running.", "status": "healthy"}

# API endpoints
@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.get("/api/test")
def test_api():
    return {"message": "API is working", "endpoints": ["/api/ping", "/api/health"]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting CRM server on port {port}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
