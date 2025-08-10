import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use environment variable for database URL (Railway provides DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://neura:neura25@localhost/postgres")

# Fix for Railway's DATABASE_URL format (they use postgres:// instead of postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 