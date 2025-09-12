#!/usr/bin/env python3
"""
Startup script for the CRM application.
This script ensures the database is properly initialized before starting the FastAPI app.
"""
import os
import sys
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_database(max_retries=30, retry_delay=2):
    """Wait for database to be available"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    # Fix Railway's DATABASE_URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    logger.info(f"Waiting for database connection...")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Database connection successful!")
                return True
        except OperationalError as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after all retries")
                return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to database: {e}")
            return False
    
    return False

def main():
    """Main startup function"""
    logger.info("Starting CRM Application...")
    
    # Wait for database to be available
    if not wait_for_database():
        logger.error("Database not available, exiting...")
        sys.exit(1)
    
    # Import and start the FastAPI app
    try:
        # Add the current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from backend.api.main import app
        import uvicorn
        
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting FastAPI server on port {port}...")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
