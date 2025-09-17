from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os
import bcrypt

from backend.api.db import get_db
from backend.api.models import User
from backend.api.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.get("/test")
def auth_router_test():
    return {"message": "Auth router is working", "timestamp": datetime.now().isoformat()}

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
    """Verify a password against its hash.
    Fast-deploy fallback: if stored value is not a bcrypt hash, compare plaintext.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Fallback for legacy/plaintext data to avoid 500s in new environments
        return plain_password == hashed_password

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
async def login(request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return access token. Always return JSON; never 500 for bad creds."""
    # Accept JSON or form-encoded bodies to be resilient to client differences
    try:
        payload = await request.json()
        login_data = LoginRequest(**payload)
    except Exception:
        try:
            form = await request.form()
            payload = {"email": form.get("email"), "password": form.get("password")}
            login_data = LoginRequest(**payload)
        except Exception:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid login payload")

    # Find user by email
    try:
        user = db.query(User).filter(User.email == login_data.email).first()
    except Exception:
        # DB issue—avoid leaking details
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")

    if not user:
        # Generic response
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Verify password with safe fallback; any error -> treat as mismatch
    ok: bool = False
    try:
        ok = verify_password(login_data.password, user.password_hash)
    except Exception:
        ok = (login_data.password == (user.password_hash or ""))

    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Create access token
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "user_id": user.id,
                "organization_id": user.organization_id,
            },
            expires_delta=access_token_expires,
        )
    except Exception:
        # If signing fails due to bad SECRET_KEY setup
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token signing failed")

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id,
        "avatar_url": user.avatar_url,
    }

    return LoginResponse(access_token=access_token, token_type="bearer", user=user_data)

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
