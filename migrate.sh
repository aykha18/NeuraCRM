#!/bin/bash
echo "Running database migrations..."

# Change to backend directory
cd backend

# Run Alembic migrations
echo "Running alembic upgrade head..."
alembic upgrade head

echo "Database migrations completed!"
