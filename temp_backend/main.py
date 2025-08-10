#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    try:
        # Import and run the FastAPI app
        from api.main import app
        import uvicorn
        
        port = int(os.getenv("PORT", 8000))
        print(f"Starting FastAPI app on port {port}")
        print(f"Python path: {sys.path}")
        
        uvicorn.run("api.main:app", host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
