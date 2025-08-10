#!/bin/bash
echo "Running database migrations..."

# Change to backend directory
cd backend

# Set the DATABASE_URL for Alembic
export DATABASE_URL="$DATABASE_URL"

# Run Alembic migrations
echo "Running alembic upgrade head..."
echo "Using DATABASE_URL: $DATABASE_URL"
alembic upgrade head

echo "Database migrations completed!"
