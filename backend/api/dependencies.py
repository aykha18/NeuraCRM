from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .db import get_session_local
from .models import User
import jwt
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_db():
    """
    Dependency that creates a new SQLAlchemy SessionLocal that will be used in a single request.
    The session is properly closed after the request is finished.
    """
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Dependency that gets the current authenticated user from JWT token
    """
    try:
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        ALGORITHM = "HS256"
        
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Try to get user_id from sub field (should be user ID)
        user_id = payload.get("sub")
        
        # If sub is not a number, try to get user_id from user_id field
        if not user_id or not str(user_id).isdigit():
            user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Eager property access to avoid lazy loading post-session
        _ = user.id; _ = user.name; _ = user.email; _ = user.role; _ = user.organization_id; _ = user.avatar_url
        
        return user
    except jwt.PyJWTError as e:
        logger.warning(f"JWT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"get_current_user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
