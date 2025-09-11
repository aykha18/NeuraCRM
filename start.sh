#!/bin/bash

# Start the application
echo "Starting CRM API server..."
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
