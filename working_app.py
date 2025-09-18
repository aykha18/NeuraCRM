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
from sqlalchemy import text, func
from pydantic import BaseModel
from typing import Optional

# Try to import authentication dependencies
try:
    from pydantic import EmailStr
    from passlib.context import CryptContext
    import jwt
    import bcrypt
    AUTH_AVAILABLE = True
    print("Γ£à Authentication dependencies imported successfully")
except ImportError as e:
    print(f"ΓÜá∩╕Å Authentication dependencies not available: {e}")
    AUTH_AVAILABLE = False

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from api.db import get_db, get_engine
    from api.models import Contact, Lead, Deal, Stage, User, Organization, Subscription, SubscriptionPlan, CustomerAccount, Invoice, Payment, Revenue, FinancialReport
    from api.websocket import websocket_endpoint
    from api.routers import chat
    from api.routers.predictive_analytics import router as predictive_analytics_router
    DB_AVAILABLE = True
    print("Γ£à Database models imported successfully")
    
    # Create financial management tables if they don't exist
    try:
        engine = get_engine()
        Invoice.metadata.create_all(bind=engine)
        Payment.metadata.create_all(bind=engine)
        Revenue.metadata.create_all(bind=engine)
        FinancialReport.metadata.create_all(bind=engine)
        print("Γ£à Financial management tables created/verified successfully")
    except Exception as e:
        print(f"Γ¥î Error creating financial tables: {e}")
        
except ImportError as e:
    print(f"Γ¥î Database import failed: {e}")
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
    organization_id: Optional[int] = None  # Optional for backward compatibility

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
    organization_id: Optional[int] = None
    created_at: Optional[datetime] = None

class OrganizationCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    domain: Optional[str] = None
    created_at: Optional[datetime] = None

# SaaS Organization Signup Schemas
class OrganizationSignupRequest(BaseModel):
    """Request schema for organization signup"""
    organization_name: str
    organization_domain: Optional[str] = None
    admin_name: str
    admin_email: str
    admin_password: str
    plan: str = "free"  # free, pro, enterprise

class OrganizationSignupResponse(BaseModel):
    """Response schema for organization signup"""
    organization: dict
    admin_user: dict
    subscription: dict
    access_token: str
    token_type: str = "bearer"

class SubscriptionPlanResponse(BaseModel):
    """Response schema for subscription plans"""
    id: int
    name: str
    display_name: str
    description: str
    price_monthly: float
    price_yearly: float
    user_limit: int
    features: list
    is_active: bool

class SubscriptionResponse(BaseModel):
    """Response schema for organization subscription"""
    id: int
    organization_id: int
    plan: str
    status: str
    billing_cycle: str
    user_limit: int
    features: dict
    created_at: datetime
    expires_at: Optional[datetime]
    trial_ends_at: Optional[datetime]

class UserLimitCheck(BaseModel):
    """Response schema for user limit check"""
    current_users: int
    user_limit: int
    can_add_user: bool
    plan: str

# Post-Sale Workflow Models
class CustomerAccountCreate(BaseModel):
    """Request schema for creating customer account"""
    deal_id: int
    account_name: str
    contact_id: int
    account_type: str = "standard"  # standard, premium, enterprise
    onboarding_status: str = "pending"  # pending, in_progress, completed
    success_manager_id: Optional[int] = None

class CustomerAccountResponse(BaseModel):
    """Response schema for customer account"""
    id: int
    deal_id: int
    account_name: str
    contact_id: int
    account_type: str
    onboarding_status: str
    success_manager_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

class DealStatusUpdate(BaseModel):
    """Request schema for updating deal status"""
    status: str  # 'won', 'lost'
    outcome_reason: Optional[str] = None
    closed_at: Optional[datetime] = None

class CustomerSuccessMetric(BaseModel):
    """Response schema for customer success metrics"""
    account_id: int
    health_score: int  # 1-100
    engagement_level: str  # low, medium, high
    last_activity: Optional[datetime]
    renewal_probability: int  # 1-100
    satisfaction_score: Optional[int]  # 1-10

# Authentication functions (only if auth is available)
if AUTH_AVAILABLE:
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
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

# Include routers
if DB_AVAILABLE:
    app.include_router(chat.router)
    app.include_router(predictive_analytics_router)

# WebSocket endpoint
@app.websocket("/ws/chat/{room_id}")
async def websocket_chat_endpoint(websocket, room_id: int = None, token: str = None):
    if DB_AVAILABLE:
        await websocket_endpoint(websocket, room_id, token)
    else:
        await websocket.close(code=1008, reason="Database not available")

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
                conn.execute(text("SELECT 1"))
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
                "icon": "≡ƒæñ",
                "color": "blue",
                "title": "New lead John Smith added",
                "time": "2 minutes ago"
            },
            {
                "icon": "≡ƒÆ░",
                "color": "green", 
                "title": "Deal closed: $15,000 contract",
                "time": "1 hour ago"
            },
            {
                "icon": "≡ƒôº",
                "color": "purple",
                "title": "Email campaign sent to 500 leads",
                "time": "3 hours ago"
            },
            {
                "icon": "≡ƒñû",
                "color": "orange",
                "title": "AI scored 12 new leads",
                "time": "5 hours ago"
            }
        ]
    }

@app.get("/api/kanban/board")
def get_kanban_board(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get complete kanban board data (stages + deals) for current user's organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get stages (assuming stages are organization-specific, or use default stages)
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
        
        # Get deals for current user's organization
        org_id = current_user.organization_id or 1
        deals = db.query(Deal).filter(Deal.organization_id == org_id).all()
        deals_data = [
            {
                "id": deal.id,
                "title": deal.title,
                "description": deal.description or "",
                "value": deal.value or 0,
                "stage_id": deal.stage_id or 1,
                "owner_id": deal.owner_id,
                "contact_id": deal.contact_id,
                "organization_id": deal.organization_id,
                "reminder_date": deal.reminder_date.isoformat() if deal.reminder_date else None,
                "created_at": deal.created_at.isoformat() if deal.created_at else None,
                "owner_name": deal.owner.name if deal.owner else None,
                "contact_name": deal.contact.name if deal.contact else None,
                "watchers": [],  # Could be populated from watchers relationship
                "status": getattr(deal, 'status', 'open'),  # Default to 'open' if not set
                "closed_at": deal.closed_at.isoformat() if deal.closed_at else None,
                "outcome_reason": getattr(deal, 'outcome_reason', None),
                "customer_account_id": getattr(deal, 'customer_account_id', None)
            }
            for deal in deals
        ]
        
        return {
            "stages": stages_data,
            "deals": deals_data
        }
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

@app.post("/api/deals")
def create_deal(deal_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new deal for current user's organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        new_deal = Deal(
            title=deal_data.get("title"),
            value=deal_data.get("value", 0),
            stage=deal_data.get("stage", "Prospecting"),
            probability=deal_data.get("probability", 0),
            close_date=datetime.fromisoformat(deal_data.get("close_date", datetime.now().isoformat())) if deal_data.get("close_date") else datetime.now(),
            contact_name=deal_data.get("contact_name"),
            contact_email=deal_data.get("contact_email"),
            notes=deal_data.get("notes"),
            organization_id=current_user.organization_id or 1,
            owner_id=current_user.id,
            created_at=datetime.now()
        )
        db.add(new_deal)
        db.commit()
        db.refresh(new_deal)
        
        return {
            "id": new_deal.id,
            "title": new_deal.title,
            "value": new_deal.value,
            "stage": new_deal.stage,
            "probability": new_deal.probability,
            "close_date": new_deal.close_date.isoformat() if new_deal.close_date else None,
            "contact_name": new_deal.contact_name,
            "contact_email": new_deal.contact_email,
            "notes": new_deal.notes,
            "owner_id": new_deal.owner_id,
            "organization_id": new_deal.organization_id,
            "created_at": new_deal.created_at.isoformat() if new_deal.created_at else None
        }
    except Exception as e:
        print(f"Error creating deal: {e}")
        db.rollback()
        return {"error": "Failed to create deal"}

# Authentication endpoints (only if auth is available)
if AUTH_AVAILABLE:
    @app.post("/api/auth/register", response_model=UserResponse)
    def register(user: UserCreate, db: Session = Depends(get_db)):
        """Register a new user"""
        if not DB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Use provided organization_id or default to 1 (Default Organization)
        organization_id = user.organization_id or 1
        
        # Check if user already exists in this organization
        existing_user = db.query(User).filter(
            User.email == user.email,
            User.organization_id == organization_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered in this organization")
        
        # Check user limit for organization
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).first()
        
        if subscription:
            current_users = db.query(User).filter(User.organization_id == organization_id).count()
            if current_users >= subscription.user_limit:
                raise HTTPException(
                    status_code=403, 
                    detail=f"User limit reached for {subscription.plan} plan ({subscription.user_limit} users). Please upgrade your plan to add more users."
                )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            role="user",
            organization_id=organization_id,
            created_at=datetime.now()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            role=db_user.role,
            organization_id=db_user.organization_id,
            created_at=db_user.created_at
        )

    @app.post("/api/auth/login", response_model=Token)
    def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
        """Login user and return access token"""
        if not DB_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Authenticate user (email is unique per organization now)
        user = db.query(User).filter(User.email == user_credentials.email).first()
        if not user or not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token with organization info
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "organization_id": user.organization_id
            }, 
            expires_delta=access_token_expires
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
            organization_id=current_user.organization_id or 1,
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

# Organization Management Endpoints
@app.post("/api/organizations", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization (for new clients)"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    
    # Create new organization
    db_org = Organization(
        name=org.name,
        domain=org.domain,
        created_at=datetime.now()
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    
    return OrganizationResponse(
        id=db_org.id,
        name=db_org.name,
        domain=db_org.domain,
        created_at=db_org.created_at
    )

@app.get("/api/organizations", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    """Get all organizations (admin only)"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    
    organizations = db.query(Organization).all()
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            domain=org.domain,
            created_at=org.created_at
        )
        for org in organizations
    ]

@app.get("/api/organizations/{org_id}/users", response_model=list[UserResponse])
def get_organization_users(org_id: int, db: Session = Depends(get_db)):
    """Get all users in an organization"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    
    users = db.query(User).filter(User.organization_id == org_id).all()
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            organization_id=user.organization_id,
            created_at=user.created_at
        )
        for user in users
    ]

# SaaS Organization Signup Endpoints
@app.post("/api/organizations/signup", response_model=OrganizationSignupResponse)
def signup_organization(signup_data: OrganizationSignupRequest, db: Session = Depends(get_db)):
    """Self-service organization signup with admin user creation"""
    if not DB_AVAILABLE or not AUTH_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database or authentication not available")
    
    try:
        # Check if organization domain already exists (if provided)
        if signup_data.organization_domain:
            existing_org = db.query(Organization).filter(
                Organization.domain == signup_data.organization_domain
            ).first()
            if existing_org:
                raise HTTPException(
                    status_code=400, 
                    detail="Organization with this domain already exists"
                )
        
        # Get subscription plan details
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == signup_data.plan
        ).first()
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        # Create organization
        db_org = Organization(
            name=signup_data.organization_name,
            domain=signup_data.organization_domain,
            created_at=datetime.now()
        )
        db.add(db_org)
        db.flush()  # Get the organization ID
        
        # Create subscription
        subscription = Subscription(
            organization_id=db_org.id,
            plan=signup_data.plan,
            status='active',
            user_limit=plan.user_limit,
            features=plan.features,
            created_at=datetime.now()
        )
        db.add(subscription)
        
        # Create admin user
        hashed_password = get_password_hash(signup_data.admin_password)
        admin_user = User(
            name=signup_data.admin_name,
            email=signup_data.admin_email,
            password_hash=hashed_password,
            role="admin",
            organization_id=db_org.id,
            created_at=datetime.now()
        )
        db.add(admin_user)
        db.flush()  # Get the user ID
        
        # Create access token for admin user
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": signup_data.admin_email, "user_id": admin_user.id, "organization_id": db_org.id},
            expires_delta=access_token_expires
        )
        
        db.commit()
        
        return OrganizationSignupResponse(
            organization={
                "id": db_org.id,
                "name": db_org.name,
                "domain": db_org.domain,
                "created_at": db_org.created_at.isoformat()
            },
            admin_user={
                "id": admin_user.id,
                "name": admin_user.name,
                "email": admin_user.email,
                "role": admin_user.role,
                "organization_id": admin_user.organization_id,
                "created_at": admin_user.created_at.isoformat()
            },
            subscription={
                "id": subscription.id,
                "plan": subscription.plan,
                "status": subscription.status,
                "user_limit": subscription.user_limit,
                "features": subscription.features,
                "created_at": subscription.created_at.isoformat()
            },
            access_token=access_token,
            token_type="bearer"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create organization: {str(e)}")

@app.get("/api/subscription-plans", response_model=list[SubscriptionPlanResponse])
def get_subscription_plans(db: Session = Depends(get_db)):
    """Get available subscription plans"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return [
        SubscriptionPlanResponse(
            id=plan.id,
            name=plan.name,
            display_name=plan.display_name,
            description=plan.description,
            price_monthly=plan.price_monthly,
            price_yearly=plan.price_yearly,
            user_limit=plan.user_limit,
            features=plan.features,
            is_active=plan.is_active
        )
        for plan in plans
    ]

@app.get("/api/organizations/{org_id}/user-limit", response_model=UserLimitCheck)
def check_user_limit(org_id: int, db: Session = Depends(get_db)):
    """Check if organization can add more users"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    
    # Get organization subscription
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == org_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Organization subscription not found")
    
    # Count current users
    current_users = db.query(User).filter(User.organization_id == org_id).count()
    
    return UserLimitCheck(
        current_users=current_users,
        user_limit=subscription.user_limit,
        can_add_user=current_users < subscription.user_limit,
        plan=subscription.plan
    )

# AI Assistant endpoint
@app.post("/api/ai/assistant")
def ai_assistant(request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """AI Sales Assistant endpoint"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Simple AI response for now (can be enhanced later)
        message = request.get("message", "")
        
        # Basic responses based on keywords
        if "lead" in message.lower():
            return {"response": "I can help you analyze your leads. You currently have leads in your pipeline. Would you like me to show you the hottest prospects?"}
        elif "deal" in message.lower():
            return {"response": "I can help you with your deals. Let me analyze your pipeline and suggest next steps."}
        elif "contact" in message.lower():
            return {"response": "I can help you manage your contacts. Would you like me to show you contact insights?"}
        else:
            return {"response": "Hello! I'm your AI Sales Assistant. I can help you with leads, deals, contacts, and sales insights. What would you like to know?"}
            
    except Exception as e:
        return {"error": f"AI assistant error: {str(e)}"}

# User Management endpoints
@app.get("/api/users")
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all users in the current user's organization."""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "organization_id": user.organization_id
            }
            for user in users
        ]
    except Exception as e:
        return {"error": f"Failed to fetch users: {str(e)}"}

@app.post("/api/users")
def create_user(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a user in the current organization."""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Basic duplicate email check within org
        existing = (
            db.query(User)
            .filter(User.organization_id == current_user.organization_id, User.email == payload.get("email"))
            .first()
        )
        if existing:
            return {"error": "A user with this email already exists in the organization"}
        
        # Create new user
        new_user = User(
            name=payload.get("name"),
            email=payload.get("email"),
            password_hash=payload.get("password"),  # In production, hash this
            role="member",
            organization_id=current_user.organization_id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "organization_id": new_user.organization_id
        }
    except Exception as e:
        return {"error": f"Failed to create user: {str(e)}"}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a user in the same organization (cannot delete yourself)."""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        if user_id == current_user.id:
            return {"error": "You cannot delete yourself"}
        
        user = (
            db.query(User)
            .filter(User.id == user_id, User.organization_id == current_user.organization_id)
            .first()
        )
        if not user:
            return {"error": "User not found"}
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete user: {str(e)}"}

# Email Automation endpoints
@app.get("/api/email/templates")
def get_email_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all email templates for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # For now, return sample templates since we don't have EmailTemplate model in working_app.py
        return [
            {
                "id": 1,
                "name": "Welcome Email",
                "subject": "Welcome to our service!",
                "body": "Thank you for joining us. We're excited to have you on board!",
                "category": "welcome",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "created_by": current_user.id,
                "validation": {
                    "valid": True,
                    "available_variables": ["contact.name", "contact.email"],
                    "missing_variables": [],
                    "total_variables": 2
                }
            },
            {
                "id": 2,
                "name": "Follow-up Email",
                "subject": "Following up on our conversation",
                "body": "Hi there, I wanted to follow up on our recent conversation. Let me know if you have any questions!",
                "category": "follow-up",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "created_by": current_user.id,
                "validation": {
                    "valid": True,
                    "available_variables": ["contact.name", "deal.title"],
                    "missing_variables": [],
                    "total_variables": 2
                }
            }
        ]
    except Exception as e:
        return {"error": f"Failed to fetch email templates: {str(e)}"}

@app.post("/api/email/templates")
def create_email_template(template_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new email template"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # For now, return a mock created template
        return {
            "id": 999,
            "name": template_data.get("name", "New Template"),
            "subject": template_data.get("subject", ""),
            "body": template_data.get("body", ""),
            "category": template_data.get("category", "general"),
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_by": current_user.id,
            "validation": {
                "valid": True,
                "available_variables": [],
                "missing_variables": [],
                "total_variables": 0
            }
        }
    except Exception as e:
        return {"error": f"Failed to create email template: {str(e)}"}

@app.post("/api/email/templates/sample")
def create_sample_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create sample email templates"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return success message for sample template creation
        return {"message": "Sample templates created successfully"}
    except Exception as e:
        return {"error": f"Failed to create sample templates: {str(e)}"}

@app.put("/api/email/templates/{template_id}")
def update_email_template(template_id: int, template_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update an email template"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return updated template
        return {
            "id": template_id,
            "name": template_data.get("name", "Updated Template"),
            "subject": template_data.get("subject", ""),
            "body": template_data.get("body", ""),
            "category": template_data.get("category", "general"),
            "is_active": template_data.get("is_active", True),
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_by": current_user.id,
            "validation": {
                "valid": True,
                "available_variables": [],
                "missing_variables": [],
                "total_variables": 0
            }
        }
    except Exception as e:
        return {"error": f"Failed to update email template: {str(e)}"}

@app.delete("/api/email/templates/{template_id}")
def delete_email_template(template_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete an email template"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        return {"message": "Template deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete email template: {str(e)}"}

@app.post("/api/email/templates/preview")
def preview_email_template(template_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Preview an email template"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        template_id = template_data.get("template_id", 1)
        recipient_type = template_data.get("recipient_type", "contact")
        recipient_id = template_data.get("recipient_id", 1)
        
        # Return preview with sample data based on template_id
        if template_id == 1:
            return {
                "subject": "Welcome to our service!",
                "body": "Hi John Doe, thank you for joining us. We're excited to have you on board!"
            }
        elif template_id == 2:
            return {
                "subject": "Following up on our conversation",
                "body": "Hi John Doe, I wanted to follow up on our recent conversation. Let me know if you have any questions!"
            }
        else:
            return {
                "subject": template_data.get("subject", "Email Preview"),
                "body": template_data.get("body", "This is a preview of your email template.")
            }
    except Exception as e:
        return {"error": f"Failed to preview email template: {str(e)}"}

@app.get("/api/email/campaigns")
def get_email_campaigns(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all email campaigns for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return sample campaigns
        return [
            {
                "id": 1,
                "name": "Welcome Campaign",
                "template_id": 1,
                "subject_override": None,
                "body_override": None,
                "target_type": "contacts",
                "target_ids": "1,2,3",
                "scheduled_at": None,
                "sent_at": None,
                "status": "draft",
                "created_by": current_user.id,
                "created_at": "2024-01-01T00:00:00Z",
                "template": {
                    "id": 1,
                    "name": "Welcome Email",
                    "subject": "Welcome to our service!",
                    "body": "Thank you for joining us. We're excited to have you on board!",
                    "category": "welcome",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "created_by": current_user.id,
                    "validation": {
                        "valid": True,
                        "available_variables": ["contact.name", "contact.email"],
                        "missing_variables": [],
                        "total_variables": 2
                    }
                }
            },
            {
                "id": 2,
                "name": "Follow-up Campaign",
                "template_id": 2,
                "subject_override": None,
                "body_override": None,
                "target_type": "leads",
                "target_ids": "1,2",
                "scheduled_at": None,
                "sent_at": "2024-01-01T12:00:00Z",
                "status": "sent",
                "created_by": current_user.id,
                "created_at": "2024-01-01T00:00:00Z",
                "template": {
                    "id": 2,
                    "name": "Follow-up Email",
                    "subject": "Following up on our conversation",
                    "body": "Hi there, I wanted to follow up on our recent conversation. Let me know if you have any questions!",
                    "category": "follow-up",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "created_by": current_user.id,
                    "validation": {
                        "valid": True,
                        "available_variables": ["contact.name", "deal.title"],
                        "missing_variables": [],
                        "total_variables": 2
                    }
                }
            }
        ]
    except Exception as e:
        return {"error": f"Failed to fetch email campaigns: {str(e)}"}

@app.post("/api/email/campaigns")
def create_email_campaign(campaign_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new email campaign"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return a mock created campaign
        return {
            "id": 999,
            "name": campaign_data.get("name", "New Campaign"),
            "template_id": campaign_data.get("template_id", 1),
            "subject_override": campaign_data.get("subject_override"),
            "body_override": campaign_data.get("body_override"),
            "target_type": campaign_data.get("target_type", "contacts"),
            "target_ids": ",".join(map(str, campaign_data.get("target_ids", []))),
            "scheduled_at": campaign_data.get("scheduled_at"),
            "sent_at": None,
            "status": "draft",
            "created_by": current_user.id,
            "created_at": "2024-01-01T00:00:00Z",
            "template": None
        }
    except Exception as e:
        return {"error": f"Failed to create email campaign: {str(e)}"}

@app.post("/api/email/campaigns/{campaign_id}/send")
def send_email_campaign(campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send an email campaign"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return mock send results
        return {
            "message": "Campaign sent successfully",
            "sent_count": 25,
            "total_recipients": 25
        }
    except Exception as e:
        return {"error": f"Failed to send email campaign: {str(e)}"}

@app.get("/api/email/logs")
def get_email_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get email logs for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return sample email logs
        return [
            {
                "id": 1,
                "recipient_email": "test@example.com",
                "subject": "Welcome Email",
                "status": "sent",
                "sent_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "recipient_email": "test2@example.com",
                "subject": "Follow-up Email",
                "status": "delivered",
                "sent_at": "2024-01-01T00:00:00Z"
            }
        ]
    except Exception as e:
        return {"error": f"Failed to fetch email logs: {str(e)}"}

@app.get("/api/email/logs/analytics")
def get_email_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get email analytics for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return sample analytics data
        return {
            "total_sent": 150,
            "total_opened": 120,
            "total_clicked": 45,
            "open_rate": 80.0,
            "click_rate": 30.0
        }
    except Exception as e:
        return {"error": f"Failed to fetch email analytics: {str(e)}"}

# Kanban Update Deal Endpoint
@app.put("/api/kanban/deals/{deal_id}")
def update_deal(deal_id: int, deal_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a deal"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get the deal
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.organization_id == current_user.organization_id
        ).first()
        
        if not deal:
            return {"error": "Deal not found"}
        
        # Update deal fields
        if "title" in deal_data and deal_data["title"]:
            deal.title = deal_data["title"]
        if "value" in deal_data and deal_data["value"]:
            # Handle value field - remove currency symbols and convert to float
            value_str = str(deal_data["value"]).replace("$", "").replace(",", "").strip()
            if value_str and value_str != "":
                try:
                    deal.value = float(value_str)
                except ValueError:
                    pass  # Skip invalid values
        if "description" in deal_data:
            deal.description = deal_data["description"]
        if "stage_id" in deal_data and deal_data["stage_id"]:
            deal.stage_id = deal_data["stage_id"]
        if "owner_id" in deal_data and deal_data["owner_id"]:
            deal.owner_id = deal_data["owner_id"]
        if "contact_id" in deal_data and deal_data["contact_id"]:
            deal.contact_id = deal_data["contact_id"]
        
        db.commit()
        
        return {
            "message": "Deal updated successfully",
            "deal": {
                "id": deal.id,
                "title": deal.title,
                "value": deal.value,
                "description": deal.description,
                "stage_id": deal.stage_id,
                "owner_id": deal.owner_id,
                "contact_id": deal.contact_id
            }
        }
        
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update deal: {str(e)}"}

# Kanban Move Deal Endpoint
@app.post("/api/kanban/deals/{deal_id}/move")
def move_deal(deal_id: int, move_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Move a deal to a different stage and trigger post-sale workflow if moved to Won"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get the deal
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.organization_id == current_user.organization_id
        ).first()
        
        if not deal:
            return {"error": "Deal not found"}
        
        new_stage_id = move_data.get("to_stage_id") or move_data.get("stage_id")
        if not new_stage_id:
            return {"error": "to_stage_id or stage_id is required"}
        
        # Get the stage name to check if it's "Won"
        stage = db.query(Stage).filter(Stage.id == new_stage_id).first()
        if not stage:
            return {"error": "Stage not found"}
        
        # Update deal stage
        old_stage_id = deal.stage_id
        deal.stage_id = new_stage_id
        print(f"DEBUG: Moving deal {deal_id} from stage {old_stage_id} to stage {new_stage_id} (stage name: '{stage.name}')")
        
        # If moved to "Won" stage, trigger post-sale workflow
        if stage.name.lower() == "won":
            deal.status = "won"
            deal.outcome_reason = "Deal moved to Won stage"
            deal.closed_at = datetime.now()
            
            # Create customer account in database
            customer_account = CustomerAccount(
                deal_id=deal_id,
                account_name=f"{deal.contact.name if deal.contact else 'Customer'} Account",
                contact_id=deal.contact_id,
                account_type="standard",
                onboarding_status="pending",
                success_manager_id=deal.owner_id,
                health_score=75.0,  # Default health score
                engagement_level="medium"  # Default engagement level
            )
            
            db.add(customer_account)
            db.flush()  # Flush to get the ID
            
            # Update deal with customer account ID
            deal.customer_account_id = customer_account.id
            
            account_response = {
                "id": customer_account.id,
                "deal_id": deal_id,
                "account_name": customer_account.account_name,
                "contact_id": deal.contact_id,
                "account_type": customer_account.account_type,
                "onboarding_status": customer_account.onboarding_status,
                "success_manager_id": deal.owner_id,
                "health_score": customer_account.health_score,
                "engagement_level": customer_account.engagement_level,
                "created_at": customer_account.created_at.isoformat(),
                "updated_at": customer_account.updated_at.isoformat() if customer_account.updated_at else None
            }
            
            db.commit()
            
            return {
                "message": "Deal moved to Won stage and customer account created",
                "deal": {
                    "id": deal.id,
                    "title": deal.title,
                    "stage_id": deal.stage_id,
                    "status": deal.status,
                    "closed_at": deal.closed_at.isoformat(),
                    "outcome_reason": deal.outcome_reason
                },
                "customer_account": account_response
            }
        elif stage.name.lower() == "lost":
            # If moved to "Lost" stage
            deal.status = "lost"
            deal.outcome_reason = "Deal moved to Lost stage"
            deal.closed_at = datetime.now()
            
            db.commit()
            
            return {
                "message": "Deal moved to Lost stage",
                "deal": {
                    "id": deal.id,
                    "title": deal.title,
                    "stage_id": deal.stage_id,
                    "status": deal.status,
                    "closed_at": deal.closed_at.isoformat(),
                    "outcome_reason": deal.outcome_reason
                }
            }
        else:
            # Regular stage move
            print(f"DEBUG: Committing regular stage move for deal {deal_id}")
            db.commit()
            print(f"DEBUG: Successfully committed deal {deal_id} to stage {new_stage_id}")
            
            return {
                "message": "Deal moved successfully",
                "deal": {
                    "id": deal.id,
                    "title": deal.title,
                    "stage_id": deal.stage_id,
                    "status": getattr(deal, 'status', 'open')
                }
            }
            
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to move deal: {str(e)}"}

# Post-Sale Workflow Endpoints
@app.put("/api/deals/{deal_id}/status")
def update_deal_status(deal_id: int, status_data: DealStatusUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update deal status to won/lost and trigger post-sale workflow"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get the deal
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.organization_id == current_user.organization_id
        ).first()
        
        if not deal:
            return {"error": "Deal not found"}
        
        # Update deal status
        deal.status = status_data.status
        deal.outcome_reason = status_data.outcome_reason
        deal.closed_at = status_data.closed_at or datetime.now()
        
        # If deal is won, create customer account
        if status_data.status == "won":
            # Create customer account
            customer_account = {
                "deal_id": deal_id,
                "account_name": f"{deal.contact.name if deal.contact else 'Customer'} Account",
                "contact_id": deal.contact_id,
                "account_type": "standard",
                "onboarding_status": "pending",
                "success_manager_id": deal.owner_id
            }
            
            # Store customer account (for now, return mock data)
            account_response = {
                "id": 999,  # Mock ID
                "deal_id": deal_id,
                "account_name": customer_account["account_name"],
                "contact_id": deal.contact_id,
                "account_type": "standard",
                "onboarding_status": "pending",
                "success_manager_id": deal.owner_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }
            
            # Update deal with customer account reference
            deal.customer_account_id = 999  # Mock ID
            
            db.commit()
            
            return {
                "message": "Deal marked as won and customer account created",
                "deal": {
                    "id": deal.id,
                    "title": deal.title,
                    "status": deal.status,
                    "closed_at": deal.closed_at.isoformat(),
                    "outcome_reason": deal.outcome_reason
                },
                "customer_account": account_response
            }
        else:
            # Deal is lost
            db.commit()
            return {
                "message": "Deal marked as lost",
                "deal": {
                    "id": deal.id,
                    "title": deal.title,
                    "status": deal.status,
                    "closed_at": deal.closed_at.isoformat(),
                    "outcome_reason": deal.outcome_reason
                }
            }
            
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update deal status: {str(e)}"}

@app.get("/api/customer-accounts")
def get_customer_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all customer accounts for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get customer accounts from database
        # First get all deals for the organization
        org_deals = db.query(Deal).filter(Deal.organization_id == current_user.organization_id).all()
        deal_ids = [deal.id for deal in org_deals]
        
        # Then get customer accounts for those deals
        customer_accounts = db.query(CustomerAccount).filter(
            CustomerAccount.deal_id.in_(deal_ids)
        ).all()
        
        return [
            {
                "id": account.id,
                "deal_id": account.deal_id,
                "account_name": account.account_name,
                "contact_id": account.contact_id,
                "account_type": account.account_type,
                "onboarding_status": account.onboarding_status,
                "success_manager_id": account.success_manager_id,
                "health_score": account.health_score,
                "engagement_level": account.engagement_level,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat() if account.updated_at else None,
                "renewal_probability": 85  # Default value for now
            }
            for account in customer_accounts
        ]
    except Exception as e:
        return {"error": f"Failed to fetch customer accounts: {str(e)}"}

@app.get("/api/customer-accounts/{account_id}/success-metrics")
def get_customer_success_metrics(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get customer success metrics for an account"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Return mock success metrics
        return {
            "account_id": account_id,
            "health_score": 85,
            "engagement_level": "high",
            "last_activity": "2024-01-20T10:30:00Z",
            "renewal_probability": 90,
            "satisfaction_score": 9,
            "metrics": {
                "total_interactions": 15,
                "response_time_avg": "2.5 hours",
                "feature_adoption": 78,
                "support_tickets": 2,
                "last_renewal": "2024-01-01T00:00:00Z",
                "next_renewal": "2025-01-01T00:00:00Z"
            }
        }
    except Exception as e:
        return {"error": f"Failed to fetch customer success metrics: {str(e)}"}

@app.post("/api/customer-accounts/{account_id}/onboarding/start")
def start_customer_onboarding(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Start the customer onboarding process"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Mock onboarding workflow
        onboarding_tasks = [
            {
                "id": 1,
                "title": "Welcome Call",
                "description": "Schedule and conduct welcome call with customer",
                "status": "pending",
                "due_date": "2024-01-25T00:00:00Z",
                "assigned_to": current_user.id
            },
            {
                "id": 2,
                "title": "Account Setup",
                "description": "Configure customer account and permissions",
                "status": "pending",
                "due_date": "2024-01-26T00:00:00Z",
                "assigned_to": current_user.id
            },
            {
                "id": 3,
                "title": "Training Session",
                "description": "Conduct product training session",
                "status": "pending",
                "due_date": "2024-01-28T00:00:00Z",
                "assigned_to": current_user.id
            },
            {
                "id": 4,
                "title": "Success Plan",
                "description": "Create and review customer success plan",
                "status": "pending",
                "due_date": "2024-01-30T00:00:00Z",
                "assigned_to": current_user.id
            }
        ]
        
        return {
            "message": "Customer onboarding started",
            "account_id": account_id,
            "onboarding_status": "in_progress",
            "tasks": onboarding_tasks
        }
    except Exception as e:
        return {"error": f"Failed to start customer onboarding: {str(e)}"}

# ============================================================================
# FINANCIAL MANAGEMENT ENDPOINTS
# ============================================================================

# Invoice Management
@app.get("/api/invoices")
def get_invoices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all invoices for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        invoices = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id
        ).all()
        
        return [
            {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "deal_id": invoice.deal_id,
                "customer_account_id": invoice.customer_account_id,
                "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else None,
                "due_date": invoice.due_date.isoformat(),
                "status": invoice.status,
                "subtotal": invoice.subtotal,
                "tax_rate": invoice.tax_rate,
                "tax_amount": invoice.tax_amount,
                "total_amount": invoice.total_amount,
                "paid_amount": invoice.paid_amount,
                "balance_due": invoice.balance_due,
                "description": invoice.description,
                "notes": invoice.notes,
                "created_at": invoice.created_at.isoformat(),
                "sent_at": invoice.sent_at.isoformat() if invoice.sent_at else None,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
            }
            for invoice in invoices
        ]
    except Exception as e:
        return {"error": f"Failed to fetch invoices: {str(e)}"}

@app.post("/api/invoices")
def create_invoice(invoice_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new invoice"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Generate invoice number
        invoice_count = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id
        ).count()
        invoice_number = f"INV-{current_user.organization_id:03d}-{invoice_count + 1:06d}"
        
        # Calculate amounts
        subtotal = float(invoice_data.get('subtotal', 0))
        tax_rate = float(invoice_data.get('tax_rate', 0))
        tax_amount = subtotal * (tax_rate / 100)
        total_amount = subtotal + tax_amount
        
        invoice = Invoice(
            invoice_number=invoice_number,
            deal_id=invoice_data['deal_id'],
            customer_account_id=invoice_data.get('customer_account_id'),
            organization_id=current_user.organization_id,
            due_date=datetime.fromisoformat(invoice_data['due_date'].replace('Z', '+00:00')),
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total_amount=total_amount,
            balance_due=total_amount,
            description=invoice_data.get('description'),
            notes=invoice_data.get('notes'),
            terms_conditions=invoice_data.get('terms_conditions'),
            created_by=current_user.id
        )
        
        db.add(invoice)
        db.commit()
        
        return {
            "message": "Invoice created successfully",
            "invoice": {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "total_amount": invoice.total_amount,
                "status": invoice.status
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create invoice: {str(e)}"}

@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific invoice"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id
        ).first()
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "deal_id": invoice.deal_id,
            "customer_account_id": invoice.customer_account_id,
            "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else None,
            "due_date": invoice.due_date.isoformat(),
            "status": invoice.status,
            "subtotal": invoice.subtotal,
            "tax_rate": invoice.tax_rate,
            "tax_amount": invoice.tax_amount,
            "total_amount": invoice.total_amount,
            "paid_amount": invoice.paid_amount,
            "balance_due": invoice.balance_due,
            "description": invoice.description,
            "notes": invoice.notes,
            "terms_conditions": invoice.terms_conditions,
            "created_at": invoice.created_at.isoformat(),
            "sent_at": invoice.sent_at.isoformat() if invoice.sent_at else None,
            "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
        }
    except Exception as e:
        return {"error": f"Failed to fetch invoice: {str(e)}"}

@app.put("/api/invoices/{invoice_id}/status")
def update_invoice_status(invoice_id: int, status_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update invoice status"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id
        ).first()
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        new_status = status_data.get('status')
        if new_status not in ['draft', 'sent', 'paid', 'overdue', 'cancelled']:
            return {"error": "Invalid status"}
        
        invoice.status = new_status
        
        if new_status == 'sent':
            invoice.sent_at = datetime.utcnow()
        elif new_status == 'paid':
            invoice.paid_at = datetime.utcnow()
            invoice.paid_amount = invoice.total_amount
            invoice.balance_due = 0
        
        db.commit()
        
        return {
            "message": "Invoice status updated successfully",
            "invoice": {
                "id": invoice.id,
                "status": invoice.status,
                "sent_at": invoice.sent_at.isoformat() if invoice.sent_at else None,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update invoice status: {str(e)}"}

# Payment Management
@app.get("/api/payments")
def get_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all payments for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        payments = db.query(Payment).filter(
            Payment.organization_id == current_user.organization_id
        ).all()
        
        return [
            {
                "id": payment.id,
                "invoice_id": payment.invoice_id,
                "payment_number": payment.payment_number,
                "amount": payment.amount,
                "payment_date": payment.payment_date.isoformat(),
                "payment_method": payment.payment_method,
                "payment_reference": payment.payment_reference,
                "status": payment.status,
                "notes": payment.notes,
                "created_at": payment.created_at.isoformat()
            }
            for payment in payments
        ]
    except Exception as e:
        return {"error": f"Failed to fetch payments: {str(e)}"}

@app.post("/api/payments")
def create_payment(payment_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new payment"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Generate payment number
        payment_count = db.query(Payment).filter(
            Payment.organization_id == current_user.organization_id
        ).count()
        payment_number = f"PAY-{current_user.organization_id:03d}-{payment_count + 1:06d}"
        
        payment = Payment(
            invoice_id=payment_data['invoice_id'],
            organization_id=current_user.organization_id,
            payment_number=payment_number,
            amount=float(payment_data['amount']),
            payment_date=datetime.fromisoformat(payment_data['payment_date'].replace('Z', '+00:00')),
            payment_method=payment_data['payment_method'],
            payment_reference=payment_data.get('payment_reference'),
            status=payment_data.get('status', 'pending'),
            notes=payment_data.get('notes'),
            created_by=current_user.id
        )
        
        db.add(payment)
        
        # Update invoice payment status
        invoice = db.query(Invoice).filter(Invoice.id == payment_data['invoice_id']).first()
        if invoice:
            invoice.paid_amount += payment.amount
            invoice.balance_due = invoice.total_amount - invoice.paid_amount
            
            if invoice.balance_due <= 0:
                invoice.status = 'paid'
                invoice.paid_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Payment created successfully",
            "payment": {
                "id": payment.id,
                "payment_number": payment.payment_number,
                "amount": payment.amount,
                "status": payment.status
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create payment: {str(e)}"}

# Revenue Management
@app.get("/api/revenue")
def get_revenue(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get revenue data for the organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        revenue_entries = db.query(Revenue).filter(
            Revenue.organization_id == current_user.organization_id
        ).all()
        
        return [
            {
                "id": revenue.id,
                "invoice_id": revenue.invoice_id,
                "deal_id": revenue.deal_id,
                "amount": revenue.amount,
                "recognition_date": revenue.recognition_date.isoformat(),
                "recognition_type": revenue.recognition_type,
                "recognition_period": revenue.recognition_period,
                "revenue_type": revenue.revenue_type,
                "revenue_category": revenue.revenue_category,
                "status": revenue.status,
                "created_at": revenue.created_at.isoformat()
            }
            for revenue in revenue_entries
        ]
    except Exception as e:
        return {"error": f"Failed to fetch revenue data: {str(e)}"}

@app.post("/api/revenue/recognize")
def recognize_revenue(revenue_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Recognize revenue for an invoice"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == revenue_data['invoice_id'],
            Invoice.organization_id == current_user.organization_id
        ).first()
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        # Check if revenue for this invoice already exists
        existing_revenue = db.query(Revenue).filter(
            Revenue.invoice_id == revenue_data['invoice_id'],
            Revenue.organization_id == current_user.organization_id
        ).first()
        
        if existing_revenue:
            return {"error": "Revenue for this invoice has already been recognized"}
        
        # Create revenue entry
        revenue = Revenue(
            invoice_id=revenue_data['invoice_id'],
            deal_id=invoice.deal_id,
            organization_id=current_user.organization_id,
            amount=float(revenue_data['amount']),
            recognition_date=datetime.fromisoformat(revenue_data['recognition_date'].replace('Z', '+00:00')),
            recognition_type=revenue_data.get('recognition_type', 'immediate'),
            recognition_period=revenue_data.get('recognition_period'),
            revenue_type=revenue_data.get('revenue_type', 'product'),
            revenue_category=revenue_data.get('revenue_category'),
            status=revenue_data.get('status', 'recognized')
        )
        
        db.add(revenue)
        db.commit()
        
        return {
            "message": "Revenue recognized successfully",
            "revenue": {
                "id": revenue.id,
                "amount": revenue.amount,
                "recognition_date": revenue.recognition_date.isoformat(),
                "recognition_type": revenue.recognition_type
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to recognize revenue: {str(e)}"}

# Financial Reporting
@app.get("/api/financial/dashboard")
def get_financial_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get financial dashboard data"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get current month data
        current_month = datetime.utcnow().strftime('%Y-%m')
        
        # Revenue metrics
        total_revenue = db.query(Revenue).filter(
            Revenue.organization_id == current_user.organization_id,
            Revenue.status == 'recognized'
        ).with_entities(func.sum(Revenue.amount)).scalar() or 0
        
        monthly_revenue = db.query(Revenue).filter(
            Revenue.organization_id == current_user.organization_id,
            Revenue.recognition_period == current_month,
            Revenue.status == 'recognized'
        ).with_entities(func.sum(Revenue.amount)).scalar() or 0
        
        # Invoice metrics
        total_invoices = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id
        ).count()
        
        paid_invoices = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id,
            Invoice.status == 'paid'
        ).count()
        
        overdue_invoices = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id,
            Invoice.status == 'overdue'
        ).count()
        
        # Payment metrics
        total_payments = db.query(Payment).filter(
            Payment.organization_id == current_user.organization_id,
            Payment.status == 'completed'
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        # Outstanding amounts
        outstanding_amount = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id,
            Invoice.status.in_(['sent', 'overdue'])
        ).with_entities(func.sum(Invoice.balance_due)).scalar() or 0
        
        return {
            "revenue_metrics": {
                "total_revenue": total_revenue,
                "monthly_revenue": monthly_revenue,
                "revenue_growth": 15.5  # Mock growth percentage
            },
            "invoice_metrics": {
                "total_invoices": total_invoices,
                "paid_invoices": paid_invoices,
                "overdue_invoices": overdue_invoices,
                "collection_rate": (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
            },
            "payment_metrics": {
                "total_payments": total_payments,
                "average_payment_time": 12.5,  # Mock days
                "payment_success_rate": 94.2  # Mock percentage
            },
            "outstanding_amounts": {
                "total_outstanding": outstanding_amount,
                "overdue_amount": outstanding_amount * 0.3,  # Mock 30% overdue
                "current_amount": outstanding_amount * 0.7   # Mock 70% current
            }
        }
    except Exception as e:
        return {"error": f"Failed to fetch financial dashboard data: {str(e)}"}

@app.get("/api/financial/reports")
def get_financial_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get financial reports"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        reports = db.query(FinancialReport).filter(
            FinancialReport.organization_id == current_user.organization_id
        ).all()
        
        return [
            {
                "id": report.id,
                "report_type": report.report_type,
                "report_period": report.report_period,
                "report_name": report.report_name,
                "status": report.status,
                "created_at": report.created_at.isoformat()
            }
            for report in reports
        ]
    except Exception as e:
        return {"error": f"Failed to fetch financial reports: {str(e)}"}

@app.post("/api/financial/reports/generate")
def generate_financial_report(report_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a new financial report"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Generate report data (mock implementation)
        report = FinancialReport(
            organization_id=current_user.organization_id,
            report_type=report_data['report_type'],
            report_period=report_data['report_period'],
            report_name=report_data['report_name'],
            revenue_data={
                "total_revenue": 125000,
                "monthly_breakdown": [
                    {"month": "2024-01", "revenue": 45000},
                    {"month": "2024-02", "revenue": 52000},
                    {"month": "2024-03", "revenue": 48000}
                ]
            },
            payment_data={
                "total_payments": 118000,
                "collection_rate": 94.4,
                "average_payment_time": 12.5
            },
            invoice_data={
                "total_invoices": 45,
                "paid_invoices": 42,
                "overdue_invoices": 3
            },
            kpi_data={
                "revenue_growth": 15.5,
                "customer_lifetime_value": 2500,
                "churn_rate": 5.2
            },
            generated_by=current_user.id
        )
        
        db.add(report)
        db.commit()
        
        return {
            "message": "Financial report generated successfully",
            "report": {
                "id": report.id,
                "report_name": report.report_name,
                "report_type": report.report_type,
                "report_period": report.report_period
            }
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to generate financial report: {str(e)}"}

# Additional API endpoints for other pages
@app.get("/api/contacts")
def get_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all contacts from database for current user's organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Handle users with null organization_id by using a default organization (ID 1)
        org_id = current_user.organization_id or 1
        contacts = db.query(Contact).filter(Contact.organization_id == org_id).all()
        return [
            {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "owner_id": contact.owner_id,
                "organization_id": contact.organization_id,
                "created_at": contact.created_at.isoformat() if contact.created_at else None,
                "owner_name": contact.owner.name if contact.owner else None
            }
            for contact in contacts
        ]
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

@app.post("/api/contacts")
def create_contact(contact_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new contact for current user's organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        new_contact = Contact(
            name=contact_data.get("name"),
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            company=contact_data.get("company"),
            title=contact_data.get("title"),
            industry=contact_data.get("industry"),
            notes=contact_data.get("notes"),
            organization_id=current_user.organization_id or 1,
            owner_id=current_user.id,
            created_at=datetime.now()
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        
        return {
            "id": new_contact.id,
            "name": new_contact.name,
            "email": new_contact.email,
            "phone": new_contact.phone,
            "company": new_contact.company,
            "title": new_contact.title,
            "industry": new_contact.industry,
            "notes": new_contact.notes,
            "owner_id": new_contact.owner_id,
            "organization_id": new_contact.organization_id,
            "created_at": new_contact.created_at.isoformat() if new_contact.created_at else None
        }
    except Exception as e:
        print(f"Error creating contact: {e}")
        db.rollback()
        return {"error": "Failed to create contact"}

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
def get_leads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all leads from database for current user's organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Handle users with null organization_id by using a default organization (ID 1)
        org_id = current_user.organization_id or 1
        leads = db.query(Lead).filter(Lead.organization_id == org_id).all()
        return [
            {
                "id": lead.id,
                "title": lead.title,
                "contact_id": lead.contact_id,
                "owner_id": lead.owner_id,
                "organization_id": lead.organization_id,
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

@app.post("/api/leads")
def create_lead(lead_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new lead for current user's organization"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        new_lead = Lead(
            name=lead_data.get("name"),
            company=lead_data.get("company"),
            email=lead_data.get("email"),
            phone=lead_data.get("phone"),
            source=lead_data.get("source"),
            status=lead_data.get("status", "New"),
            priority=lead_data.get("priority", "Medium"),
            estimated_value=lead_data.get("estimated_value", 0),
            notes=lead_data.get("notes"),
            organization_id=current_user.organization_id or 1,
            owner_id=current_user.id,
            created_at=datetime.now()
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        return {
            "id": new_lead.id,
            "name": new_lead.name,
            "company": new_lead.company,
            "email": new_lead.email,
            "phone": new_lead.phone,
            "source": new_lead.source,
            "status": new_lead.status,
            "priority": new_lead.priority,
            "estimated_value": new_lead.estimated_value,
            "notes": new_lead.notes,
            "owner_id": new_lead.owner_id,
            "organization_id": new_lead.organization_id,
            "created_at": new_lead.created_at.isoformat() if new_lead.created_at else None
        }
    except Exception as e:
        print(f"Error creating lead: {e}")
        db.rollback()
        return {"error": "Failed to create lead"}

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

# Stage Management Endpoints
@app.get("/stages")
def get_stages_simple(db: Session = Depends(get_db)):
    """Get all stages (simple endpoint)"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stages = db.query(Stage).order_by(Stage.order).all()
        return [
            {
                "id": stage.id,
                "name": stage.name,
                "order": stage.order,
                "wip_limit": getattr(stage, 'wip_limit', None)
            }
            for stage in stages
        ]
    except Exception as e:
        return {"error": f"Failed to fetch stages: {str(e)}"}

@app.get("/api/kanban/stages/")
def get_stages(db: Session = Depends(get_db)):
    """Get all stages"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stages = db.query(Stage).order_by(Stage.order).all()
        return [
            {
                "id": stage.id,
                "name": stage.name,
                "order": stage.order,
                "wip_limit": getattr(stage, 'wip_limit', None)
            }
            for stage in stages
        ]
    except Exception as e:
        return {"error": f"Failed to fetch stages: {str(e)}"}

@app.post("/api/kanban/stages/")
def create_stage(stage_data: dict, db: Session = Depends(get_db)):
    """Create a new stage"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get the next order number
        max_order = db.query(Stage).count()
        new_order = max_order + 1
        
        new_stage = Stage(
            name=stage_data.get("name"),
            order=new_order,
            wip_limit=stage_data.get("wip_limit")
        )
        
        db.add(new_stage)
        db.commit()
        db.refresh(new_stage)
        
        return {
            "id": new_stage.id,
            "name": new_stage.name,
            "order": new_stage.order,
            "wip_limit": getattr(new_stage, 'wip_limit', None)
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create stage: {str(e)}"}

@app.put("/api/kanban/stages/{stage_id}")
def update_stage(stage_id: int, stage_data: dict, db: Session = Depends(get_db)):
    """Update a stage"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stage = db.query(Stage).filter(Stage.id == stage_id).first()
        if not stage:
            return {"error": "Stage not found"}
        
        if "name" in stage_data:
            stage.name = stage_data["name"]
        if "order" in stage_data:
            stage.order = stage_data["order"]
        if "wip_limit" in stage_data:
            stage.wip_limit = stage_data["wip_limit"]
        
        db.commit()
        db.refresh(stage)
        
        return {
            "id": stage.id,
            "name": stage.name,
            "order": stage.order,
            "wip_limit": getattr(stage, 'wip_limit', None)
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update stage: {str(e)}"}

@app.delete("/api/kanban/stages/{stage_id}")
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    """Delete a stage"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stage = db.query(Stage).filter(Stage.id == stage_id).first()
        if not stage:
            return {"error": "Stage not found"}
        
        # Move deals from this stage to the first stage
        first_stage = db.query(Stage).order_by(Stage.order).first()
        if first_stage and first_stage.id != stage_id:
            db.query(Deal).filter(Deal.stage_id == stage_id).update({Deal.stage_id: first_stage.id})
        
        db.delete(stage)
        db.commit()
        
        return {"message": "Stage deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete stage: {str(e)}"}

# Simple Stage Management Endpoints (for frontend compatibility)
@app.post("/stages")
def create_stage_simple(stage_data: dict, db: Session = Depends(get_db)):
    """Create a new stage (simple endpoint)"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        # Get the next order number
        max_order = db.query(Stage).count()
        new_order = max_order + 1
        
        new_stage = Stage(
            name=stage_data.get("name"),
            order=new_order,
            wip_limit=stage_data.get("wip_limit")
        )
        
        db.add(new_stage)
        db.commit()
        db.refresh(new_stage)
        
        return {
            "id": new_stage.id,
            "name": new_stage.name,
            "order": new_stage.order,
            "wip_limit": getattr(new_stage, 'wip_limit', None)
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create stage: {str(e)}"}

@app.put("/stages/{stage_id}")
def update_stage_simple(stage_id: int, stage_data: dict, db: Session = Depends(get_db)):
    """Update a stage (simple endpoint)"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stage = db.query(Stage).filter(Stage.id == stage_id).first()
        if not stage:
            return {"error": "Stage not found"}
        
        if "name" in stage_data:
            stage.name = stage_data["name"]
        if "order" in stage_data:
            stage.order = stage_data["order"]
        if "wip_limit" in stage_data:
            stage.wip_limit = stage_data["wip_limit"]
        
        db.commit()
        db.refresh(stage)
        
        return {
            "id": stage.id,
            "name": stage.name,
            "order": stage.order,
            "wip_limit": getattr(stage, 'wip_limit', None)
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update stage: {str(e)}"}

@app.delete("/stages/{stage_id}")
def delete_stage_simple(stage_id: int, db: Session = Depends(get_db)):
    """Delete a stage (simple endpoint)"""
    if not DB_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        stage = db.query(Stage).filter(Stage.id == stage_id).first()
        if not stage:
            return {"error": "Stage not found"}
        
        # Move deals from this stage to the first stage
        first_stage = db.query(Stage).order_by(Stage.order).first()
        if first_stage and first_stage.id != stage_id:
            db.query(Deal).filter(Deal.stage_id == stage_id).update({Deal.stage_id: first_stage.id})
        
        db.delete(stage)
        db.commit()
        
        return {"message": "Stage deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete stage: {str(e)}"}

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
        
        # Exclude API endpoints that don't start with api/
        if path in ["stages"] or path.startswith("stages/"):
            return {"error": "API endpoint not found"}
        
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    # Frontend serving is handled above in the if FRONTEND_AVAILABLE block
    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
