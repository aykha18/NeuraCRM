#!/usr/bin/env python3
"""
Main entry point for the CRM application.
This file is used for deployment to ensure proper module resolution.
"""

import uvicorn
from backend.api.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
