#!/bin/bash

# Initialize database tables
echo "Initializing database..."
cd backend
python -c "
from api.db import engine
from api.models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('Database tables created successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    # Continue anyway, the app might still work
"

# Start the application
echo "Starting CRM API server..."
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
