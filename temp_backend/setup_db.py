#!/usr/bin/env python3
"""
Database setup script for Railway deployment
"""
import os
import sys
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command

def setup_database():
    """Set up the database with migrations"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL not found in environment variables")
            return False
        
        # Fix Railway's DATABASE_URL format
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")
        
        # Run migrations
        print("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
