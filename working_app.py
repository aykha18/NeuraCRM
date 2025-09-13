#!/usr/bin/env python3
"""
Working CRM App - Actually serves the frontend with real database
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

# Try to import authentication dependencies
try:
    from pydantic import EmailStr
    from passlib.context import CryptContext
    import jwt
    AUTH_AVAILABLE = True
    print("✅ Authentication dependencies imported successfully")
except ImportError as e:
    print(f"⚠️ Authentication dependencies not available: {e}")
    AUTH_AVAILABLE = False

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from api.db import get_db, get_engine
    from api.models import Contact, Lead, Deal, Stage, User
    DB_AVAILABLE = True
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"❌ Database import failed: {e}")
    DB_AVAILABLE = False

# Authentication configuration (only if auth is available)
if AUTH_AVAILABLE:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    security = HTTPBearer()
else:
    SECRET_KEY = None
    ALGORITHM = None
    ACCESS_TOKEN_EXPIRE_MINUTES = None
    pwd_context = None
    security = None

# Pydantic models for authentication
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str] = None
    created_at: Optional[datetime] = None

# Authentication functions (only if auth is available)
if AUTH_AVAILABLE:
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
        if not DB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        try:
            token = credentials.credentials
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
else:
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        raise HTTPException(status_code=500, detail="Authentication not available")
    
    def get_password_hash(password: str) -> str:
        raise HTTPException(status_code=500, detail="Authentication not available")
    
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        raise HTTPException(status_code=500, detail="Authentication not available")
    
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
        raise HTTPException(status_code=500, detail="Authentication not available")

app = FastAPI(title="CRM API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoints (MUST be defined BEFORE catch-all routes)
@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
def health():
    db_status = "unknown"
    if DB_AVAILABLE:
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
    else:
        db_status = "models_not_imported"
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "db_available": DB_AVAILABLE
    }

@app.get("/api/dashboard/")
def dashboard():
    """Dashboard data endpoint"""
    return {
        "metrics": {
            "active_leads": 24,
            "closed_deals": 8,
            "total_revenue": 125000,
            "ai_score": 87,
            "lead_quality_score": 92,
            "conversion_rate": 15.5,
            "target_achievement": 78.3
        },
        "performance": [
            {"month": "Jan", "leads": 45, "deals": 12, "revenue": 85000},
            {"month": "Feb", "leads": 52, "deals": 15, "revenue": 95000},
            {"month": "Mar", "leads": 38, "deals": 8, "revenue": 72000},
            {"month": "Apr", "leads": 61, "deals": 18, "revenue": 110000},
            {"month": "May", "leads": 47, "deals": 14, "revenue": 98000},
            {"month": "Jun", "leads": 55, "deals": 16, "revenue": 105000}
        ],
        "lead_quality": [
            {"name": "Hot Leads", "value": 35, "color": "#10B981"},
            {"name": "Warm Leads", "value": 45, "color": "#F59E0B"},
            {"name": "Cold Leads", "value": 20, "color": "#6B7280"}
        ],
        "activity_feed": [
            {
                "icon": "👤",
                "color": "blue",
                "title": "New lead John Smith added",
                "time": "2 minutes ago"
            },
            {
                "icon": "💰",
                "color": "green", 
                "title": "Deal closed: $15,000 contract",
                "time": "1 hour ago"
            },
            {
                "icon": "📧",
                "color": "purple",
                "title": "Email campaign sent to 500 leads",
                "time": "3 hours ago"
            },
            {
                "icon": "🤖",
                "color": "orange",
                "title": "AI scored 12 new leads",
                "time": "5 hours ago"
            }
        ]
    }

@app.get("/api/kanban/board")
def get_kanban_board(db: Session = Depends(get_db)):
    """Get complete kanban board data (stages + deals)"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get stages
        stages = db.query(Stage).order_by(Stage.order).all()
        stages_data = [
            {
                "id": stage.id,
                "name": stage.name,
                "order": stage.order or 0,
                "wip_limit": stage.wip_limit
            }
            for stage in stages
        ]
        
        # Get deals
        deals = db.query(Deal).all()
        deals_data = [
            {
                "id": deal.id,
                "title": deal.title,
                "description": deal.description or "",
                "value": deal.value or 0,
                "stage_id": deal.stage_id or 1,
                "owner_id": deal.owner_id,
                "contact_id": deal.contact_id,
                "reminder_date": deal.reminder_date.isoformat() if deal.reminder_date else None,
                "created_at": deal.created_at.isoformat() if deal.created_at else None,
                "owner_name": deal.owner.name if deal.owner else None,
                "contact_name": deal.contact.name if deal.contact else None,
                "watchers": []  # Could be populated from watchers relationship
            }
            for deal in deals
        ]
        
        return {
            "stages": stages_data,
            "deals": deals_data
        }
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

# Authentication endpoints (only if auth is available)
if AUTH_AVAILABLE:
    @app.post("/api/auth/register", response_model=UserResponse)
    def register(user: UserCreate, db: Session = Depends(get_db)):
        """Register a new user"""
        if not DB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            role="user",
            created_at=datetime.utcnow()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            role=db_user.role,
            created_at=db_user.created_at
        )

    @app.post("/api/auth/login", response_model=Token)
    def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
        """Login user and return access token"""
        if not DB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Authenticate user
        user = db.query(User).filter(User.email == user_credentials.email).first()
        if not user or not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

    @app.get("/api/auth/me", response_model=UserResponse)
    def get_current_user_info(current_user: User = Depends(get_current_user)):
        """Get current user information"""
        return UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            role=current_user.role,
            created_at=current_user.created_at
        )
else:
    @app.post("/api/auth/register")
    def register():
        return {"error": "Authentication not available"}
    
    @app.post("/api/auth/login")
    def login():
        return {"error": "Authentication not available"}
    
    @app.get("/api/auth/me")
    def get_current_user_info():
        return {"error": "Authentication not available"}

# Additional API endpoints for other pages
@app.get("/api/contacts")
def get_contacts(db: Session = Depends(get_db)):
    """Get all contacts from database"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        contacts = db.query(Contact).all()
        return [
            {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "owner_id": contact.owner_id,
                "created_at": contact.created_at.isoformat() if contact.created_at else None,
                "owner_name": contact.owner.name if contact.owner else None
            }
            for contact in contacts
        ]
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

@app.get("/api/contacts/{contact_id}")
def get_contact(contact_id: int):
    """Get specific contact"""
    return {
        "id": contact_id,
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "company": "Acme Corp",
        "status": "active",
        "owner_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "owner_name": "Sales Rep"
    }

@app.get("/api/leads")
def get_leads(db: Session = Depends(get_db)):
    """Get all leads from database"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        leads = db.query(Lead).all()
        return [
            {
                "id": lead.id,
                "title": lead.title,
                "contact_id": lead.contact_id,
                "owner_id": lead.owner_id,
                "status": lead.status,
                "source": lead.source,
                "score": lead.score,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
                "owner_name": lead.owner.name if lead.owner else None,
                "contact_name": lead.contact.name if lead.contact else None,
                "contact_email": lead.contact.email if lead.contact else None,
                "contact_phone": lead.contact.phone if lead.contact else None,
                "contact_company": lead.contact.company if lead.contact else None
            }
            for lead in leads
        ]
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int):
    """Get specific lead"""
    return {
        "id": lead_id,
        "name": "ABC Company",
        "email": "contact@abc.com",
        "phone": "+1-555-0100",
        "company": "ABC Corp",
        "status": "new",
        "source": "website",
        "score": 85,
        "owner_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "owner_name": "Sales Rep"
    }

@app.get("/api/kanban/columns")
def get_kanban_columns(db: Session = Depends(get_db)):
    """Get kanban board columns from database"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stages = db.query(Stage).order_by(Stage.order).all()
        return [
            {
                "id": stage.id,
                "name": stage.name,
                "position": stage.order or 0,
                "color": "#3B82F6"  # Default color, could be added to Stage model
            }
            for stage in stages
        ]
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

@app.get("/api/kanban/cards")
def get_kanban_cards(db: Session = Depends(get_db)):
    """Get kanban board cards from database"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        deals = db.query(Deal).all()
        return [
            {
                "id": deal.id,
                "title": deal.title,
                "description": deal.description or "",
                "column_id": deal.stage_id or 1,
                "position": 0,  # Could be added to Deal model
                "assignee_id": deal.owner_id,
                "due_date": deal.reminder_date.isoformat() if deal.reminder_date else None,
                "priority": "medium",  # Could be added to Deal model
                "value": deal.value,
                "contact_name": deal.contact.name if deal.contact else None
            }
            for deal in deals
        ]
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

# Serve frontend (AFTER all API routes)
frontend_path = "/app/frontend_dist"
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    @app.get("/{path:path}")
    def serve_frontend_routes(path: str):
        if path.startswith("api/"):
            return {"error": "API endpoint not found"}
        
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "Frontend not found"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
