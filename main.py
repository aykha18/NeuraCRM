#!/usr/bin/env python3
"""
Main entry point for the CRM application.
This file is used for deployment to ensure proper module resolution.
"""

import os
import sys
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.api.main import app
    print("Successfully imported app")
except Exception as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
