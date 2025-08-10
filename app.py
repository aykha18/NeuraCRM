#!/usr/bin/env python3
"""
App entry point for Railway deployment
"""
import os
import sys
import subprocess
import time

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("Starting CRM application...")
print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")

# Run migrations in background if DATABASE_URL is set
if os.getenv("DATABASE_URL"):
    print("Running database migrations...")
    try:
        result = subprocess.run(["./migrate.sh"], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("Database migrations completed successfully!")
        else:
            print(f"Migration warning: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Migration timeout - continuing anyway")
    except Exception as e:
        print(f"Migration error: {e} - continuing anyway")
else:
    print("No DATABASE_URL - skipping migrations")

# Import the full FastAPI app with database functionality
from api.main import app
print("Successfully imported full FastAPI app with database")

# This allows Railway to detect this as a FastAPI app
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting FastAPI app on port {port}")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Error starting uvicorn: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
