#!/bin/bash
echo "Starting backend application..."
cd backend
python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
