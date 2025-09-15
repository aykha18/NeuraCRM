from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os
import bcrypt

from ..db import get_db
from ..models import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization_id: int
    avatar_url: str = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "user_id": user.id,
                "organization_id": user.organization_id
            }, 
            expires_delta=access_token_expires
        )
        
        # Return user data
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id,
            "avatar_url": user.avatar_url
        }
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user information"""
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
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id,
            "avatar_url": user.avatar_url
        }
        
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

@router.get("/test")
async def test_endpoint():
    """Test endpoint to check if auth router is working"""
    return {"message": "Auth router is working", "status": "ok"}

@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Successfully logged out"}
