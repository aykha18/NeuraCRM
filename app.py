#!/usr/bin/env python3
"""
App entry point for Railway deployment
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    # Import the full FastAPI app with database functionality
    from api.main import app
    print("Successfully imported full FastAPI app with database")
except Exception as e:
    print(f"Error importing full app: {e}")
    import traceback
    traceback.print_exc()
    # Don't fallback to simple app - force database connection
    sys.exit(1)

# This allows Railway to detect this as a FastAPI app
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting FastAPI app on port {port}")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
    
    # Test database connection
    try:
        from api.db import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Error starting uvicorn: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
