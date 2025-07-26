from sqlalchemy.orm import Session
from .db import SessionLocal

def get_db():
    """
    Dependency that creates a new SQLAlchemy SessionLocal that will be used in a single request.
    The session is properly closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
