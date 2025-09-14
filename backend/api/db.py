import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use environment variable for database URL (Railway provides DATABASE_URL)
# Default to local PostgreSQL if no DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:aykha123@localhost/postgres")

print(f"Original DATABASE_URL: {DATABASE_URL}")

# Fix for Railway's DATABASE_URL format (they use postgres:// instead of postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"Fixed DATABASE_URL: {DATABASE_URL}")

# Create engine lazily to avoid connection issues during import
engine = None
SessionLocal = None

def get_engine():
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL)
    return engine

def get_session_local():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close() 