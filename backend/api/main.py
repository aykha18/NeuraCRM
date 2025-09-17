from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database and models first
from api.db import get_session_local, get_engine
from api.models import Lead, Contact, User, Organization, Base, Stage, Deal
from api.dependencies import get_current_user
from api.routers.auth import login as auth_login

# Import Pydantic models
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="CRM API",
    description="API for the CRM Application with AI Features",
    version="1.0.0"
)

# Global JSON error handler to avoid HTML/plain text 500s reaching the client
@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception):
    try:
        logger.error(f"Unhandled error: {exc}")
    except Exception:
        pass
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# Import and include routers immediately
try:
    from api.routers import kanban
    from api.routers.dashboard import router as dashboard_router
    from api.routers.ai import router as ai_router
    from api.routers.ai_enhanced import router as ai_enhanced_router
    from api.routers.email_automation import router as email_automation_router
    from api.routers.auth import router as auth_router
    from api.routers.chat import router as chat_router
    from api.routers.predictive_analytics import router as predictive_analytics_router
    from api.routers.users import router as users_router
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(kanban.router)
    app.include_router(dashboard_router)
    app.include_router(chat_router)
    app.include_router(ai_router)
    app.include_router(ai_enhanced_router)  # Enhanced AI with full CRM integration
    app.include_router(email_automation_router)
    app.include_router(predictive_analytics_router)
    app.include_router(users_router)
    
    logger.info("All routers loaded successfully!")
    
except Exception as e:
    logger.warning(f"Some routers failed to load: {e}")
    # Continue without the problematic routers

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables if they don't exist"""
    try:
        logger.info("Starting up CRM API...")
        
        # Test database connection
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized!")
        
        # Import lead scoring service after database is ready
        try:
            from api.lead_scoring import lead_scoring_service
            logger.info("Lead scoring service loaded successfully!")
        except Exception as e:
            logger.warning(f"Lead scoring service failed to load: {e}")
            # Continue without the lead scoring service
        
        logger.info("CRM API startup completed successfully!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Don't raise the exception, let the app start anyway
        # The health check endpoints will still work

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://192.168.1.36:5173",  # local LAN dev origin
        "https://neuracrm.up.railway.app",  # Your Railway backend
        "https://*.railway.app",  # Allow Railway domains
        "https://*.up.railway.app",  # Allow Railway domains
        # Removed "*" to ensure credentials work and proper CORS headers are sent
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Serve static files (frontend) if they exist
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend_dist")
logger.info(f"Looking for frontend at: {frontend_dist_path}")
logger.info(f"Frontend dist exists: {os.path.exists(frontend_dist_path)}")

if os.path.exists(frontend_dist_path):
    logger.info("Mounting static files and serving frontend")
    # Serve the built frontend. The Vite build expects assets under /assets and vite.svg at /vite.svg
    app.mount("/static", StaticFiles(directory=frontend_dist_path), name="static")
    assets_dir = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    vite_svg_path = os.path.join(frontend_dist_path, "vite.svg")
    if os.path.exists(vite_svg_path):
        @app.get("/vite.svg")
        async def vite_svg():
            return FileResponse(vite_svg_path)
else:
    logger.info("Frontend dist directory not found - serving API only")

class Message(BaseModel):
    user: str
    content: str

# Pydantic schema for richer Lead output
class LeadOut(BaseModel):
    id: int
    title: str
    status: str
    source: str
    created_at: datetime
    contact_name: str | None = None
    company: str | None = None
    owner_name: str | None = None
    # Lead scoring fields
    score: int | None = None
    score_updated_at: datetime | None = None
    score_factors: str | None = None
    score_confidence: float | None = None
    class Config:
        from_attributes = True

class LeadUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    source: str | None = None
    contact_id: int | None = None
    owner_id: int | None = None

# Pydantic schema for Contact output
class ContactOut(BaseModel):
    id: int
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    created_at: datetime | None = None
    owner_name: str | None = None
    class Config:
        from_attributes = True

# Pydantic schema for Contact updates
class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    owner_id: int | None = None

# Pydantic schema for Organization output
class OrganizationOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    """Serve the frontend index.html at root"""
    if os.path.exists(frontend_dist_path):
        index_path = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # Fallback to JSON if frontend not available
    return {"message": "CRM API is running.", "status": "healthy"}

# SPA catch‑all to serve client routes like /signin, without touching /api/*
# Temporarily disabled to fix API routing issues
# if os.path.exists(frontend_dist_path):
#     @app.get("/{full_path:path}")
#     def serve_spa_routes(full_path: str):
#         # Do not intercept API calls - let them pass through to the API routes
#         if full_path.startswith("api/"):
#             raise HTTPException(status_code=404, detail="API endpoint not found")
#         # Serve static file if it exists
#         candidate = os.path.join(frontend_dist_path, full_path)
#         if os.path.exists(candidate) and os.path.isfile(candidate):
#             return FileResponse(candidate)
#         # Otherwise, return index.html for SPA routing
#         index_path = os.path.join(frontend_dist_path, "index.html")
#         if os.path.exists(index_path):
#             return FileResponse(index_path)
#         raise HTTPException(status_code=404, detail="Not Found")

# Removed SPA catch-all to avoid conflicting with /api/* methods during POST

@app.post("/login")
async def legacy_login_compat(request: Request):
    """Compatibility endpoint for clients calling POST /login.
    Forwards to the actual auth login handler.
    """
    db = get_session_local()()
    try:
        return await auth_login(None, request, db)  # reuse auth logic
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.get("/api/test")
def test_api():
    return {"message": "API is working", "endpoints": ["/api/leads", "/api/contacts", "/api/leads/scoring-analytics"]}

@app.get("/api/ping")
def ping():
    """Simple health check endpoint that doesn't require database"""
    return {"status": "ok", "message": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy", 
            "message": "Service is running",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Health check failed: {e}")
        return {
            "status": "degraded", 
            "message": "Service is running but database connection failed",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Organizations endpoint (for OrganizationSelector)
@app.get("/api/organizations", response_model=list[OrganizationOut])
def list_organizations(current_user: User = Depends(get_current_user)):
    """Return the current user's organization. In multi-tenant mode we do not expose other orgs."""
    db: Session = get_session_local()()
    try:
        org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
        if not org:
            return []
        return [org]
    finally:
        db.close()

# Lead Scoring Endpoints
@app.post("/api/leads/{lead_id}/score")
def score_lead(lead_id: int):
    """Calculate and update lead score"""
    try:
        # Try to import lead scoring service
        from api.lead_scoring import lead_scoring_service
    except ImportError:
        raise HTTPException(status_code=503, detail="Lead scoring service not available")
    
    db: Session = get_session_local()()
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            db.close()
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Calculate score
        scoring_result = lead_scoring_service.calculate_lead_score(lead, db)
        
        # Update lead with new score
        lead.score = scoring_result["score"]
        lead.score_updated_at = datetime.now()
        lead.score_factors = json.dumps(scoring_result["factors"])
        lead.score_confidence = scoring_result["confidence"]
        
        db.commit()
        db.refresh(lead)
        
        db.close()
        return scoring_result
        
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to score lead: {str(e)}")

@app.post("/api/leads/score-all")
def score_all_leads():
    """Score all leads in the system"""
    try:
        # Try to import lead scoring service
        from api.lead_scoring import lead_scoring_service
    except ImportError:
        raise HTTPException(status_code=503, detail="Lead scoring service not available")
    
    db: Session = get_session_local()()
    
    try:
        leads = db.query(Lead).all()
        results = []
        
        for lead in leads:
            scoring_result = lead_scoring_service.calculate_lead_score(lead, db)
            
            # Update lead
            lead.score = scoring_result["score"]
            lead.score_updated_at = datetime.now()
            lead.score_factors = json.dumps(scoring_result["factors"])
            lead.score_confidence = scoring_result["confidence"]
            
            results.append({
                "lead_id": lead.id,
                "title": lead.title,
                "score": scoring_result["score"],
                "category": scoring_result["category"]
            })
        
        db.commit()
        db.close()
        
        return {
            "message": f"Scored {len(results)} leads",
            "results": results
        }
        
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to score leads: {str(e)}")

@app.get("/api/leads/scoring-analytics")
def get_scoring_analytics():
    """Get lead scoring analytics"""
    db: Session = get_session_local()()
    
    try:
        # Get all leads with scores
        leads = db.query(Lead).filter(Lead.score.isnot(None)).all()
        
        if not leads:
            db.close()
            return {
                "total_leads": 0,
                "average_score": 0,
                "score_distribution": {},
                "top_scoring_leads": []
            }
        
        # Calculate analytics
        scores = [lead.score for lead in leads]
        average_score = sum(scores) / len(scores)
        
        # Score distribution
        distribution = {
            "Hot (80-100)": len([s for s in scores if s >= 80]),
            "Warm (60-79)": len([s for s in scores if 60 <= s < 80]),
            "Lukewarm (40-59)": len([s for s in scores if 40 <= s < 60]),
            "Cold (0-39)": len([s for s in scores if s < 40])
        }
        
        # Top scoring leads
        top_leads = sorted(leads, key=lambda x: x.score, reverse=True)[:5]
        top_scoring_leads = [
            {
                "id": lead.id,
                "title": lead.title,
                "score": lead.score,
                "status": lead.status
            }
            for lead in top_leads
        ]
        
        db.close()
        
        return {
            "total_leads": len(leads),
            "average_score": round(average_score, 2),
            "score_distribution": distribution,
            "top_scoring_leads": top_scoring_leads
        }
        
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.post("/chat/")
def chat_with_ai(message: Message):
    # This would call OpenAI or local LLM in real usage
    return {"response": f"AI response to: '{message.content}' from {message.user}"}

# POST /api/leads endpoint (create new lead)
@app.post("/api/leads", response_model=LeadOut)
def create_lead(lead_data: LeadUpdate, current_user: User = Depends(get_current_user)):
    db: Session = get_session_local()()
    
    try:
        # Create new lead
        new_lead = Lead(
            title=lead_data.title,
            status=lead_data.status or "new",
            source=lead_data.source or "manual",
            contact_id=lead_data.contact_id or 1,  # Default to contact 1
            owner_id=lead_data.owner_id or current_user.id,  # Default to current user
            organization_id=current_user.organization_id,  # Set to current user's organization
            created_at=datetime.now()
        )
        
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        # Return with joined info
        result = (
            db.query(
                Lead.id,
                Lead.title,
                Lead.status,
                Lead.source,
                Lead.created_at,
                Contact.name.label("contact_name"),
                Contact.company.label("company"),
                User.name.label("owner_name")
            )
            .join(Contact, Lead.contact_id == Contact.id)
            .join(User, Lead.owner_id == User.id)
            .filter(Lead.id == new_lead.id)
            .first()
        )
        
        if result:
            db.close()
            return dict(result._mapping)
        else:
            # Fallback if join fails - return basic lead info
            db.close()
            return {
                "id": new_lead.id,
                "title": new_lead.title,
                "status": new_lead.status,
                "source": new_lead.source,
                "created_at": new_lead.created_at,
                "contact_name": None,
                "company": None,
                "owner_name": None
            }
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")

# POST /api/leads/{lead_id}/convert-to-deal endpoint
@app.post("/api/leads/{lead_id}/convert-to-deal")
def convert_lead_to_deal(lead_id: int, current_user: User = Depends(get_current_user)):
    """Convert a lead to a deal and add it to the Kanban board"""
    db: Session = get_session_local()()
    
    try:
        # Get the lead
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.organization_id == current_user.organization_id
        ).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get the first stage (usually "Prospecting" or "New")
        first_stage = db.query(Stage).order_by(Stage.order).first()
        if not first_stage:
            raise HTTPException(status_code=500, detail="No stages found in the system")
        
        # Create a new deal from the lead
        new_deal = Deal(
            title=lead.title,
            description=f"Converted from lead: {lead.title}",
            value=0.0,  # Default value, can be updated later
            contact_id=lead.contact_id,
            owner_id=lead.owner_id,
            stage_id=first_stage.id,
            organization_id=lead.organization_id,
            created_at=datetime.now()
        )
        
        db.add(new_deal)
        
        # Update lead status to "converted"
        lead.status = "converted"
        
        db.commit()
        db.refresh(new_deal)
        
        # Return the created deal
        return {
            "id": new_deal.id,
            "title": new_deal.title,
            "description": new_deal.description,
            "value": new_deal.value,
            "stage_id": new_deal.stage_id,
            "stage_name": first_stage.name,
            "contact_id": new_deal.contact_id,
            "owner_id": new_deal.owner_id,
            "created_at": new_deal.created_at,
            "message": f"Lead '{lead.title}' successfully converted to deal"
        }
        
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to convert lead to deal: {str(e)}")
    finally:
        db.close()

# POST /api/contacts/{contact_id}/convert-to-lead endpoint
@app.post("/api/contacts/{contact_id}/convert-to-lead")
def convert_contact_to_lead(contact_id: int, current_user: User = Depends(get_current_user)):
    """Convert a contact to a lead"""
    db: Session = get_session_local()()
    
    try:
        # Get the contact
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.organization_id == current_user.organization_id
        ).first()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Create a new lead from the contact
        new_lead = Lead(
            title=f"{contact.name} - {contact.company}",
            status="new",
            source="contact_conversion",
            contact_id=contact.id,
            owner_id=current_user.id,
            organization_id=current_user.organization_id,
            created_at=datetime.now()
        )
        
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        # Return the created lead
        return {
            "id": new_lead.id,
            "title": new_lead.title,
            "status": new_lead.status,
            "source": new_lead.source,
            "contact_id": new_lead.contact_id,
            "owner_id": new_lead.owner_id,
            "created_at": new_lead.created_at,
            "message": f"Lead created from contact: {contact.name}"
        }
        
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to convert contact to lead: {str(e)}")
    finally:
        db.close()

# GET /api/leads endpoint (with joins)
@app.get("/api/leads", response_model=list[LeadOut])
def get_leads(current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"=== LEADS API CALLED ===")
        logger.info(f"User {current_user.id} (org {current_user.organization_id}) requesting leads")
        db: Session = get_session_local()()
        # Try to get leads with joins, fallback to simple query if joins fail
        try:
            leads = (
                db.query(
                    Lead.id,
                    Lead.title,
                    Lead.status,
                    Lead.source,
                    Lead.created_at,
                    Lead.score,
                    Lead.score_updated_at,
                    Lead.score_factors,
                    Lead.score_confidence,
                    Contact.name.label("contact_name"),
                    Contact.company.label("company"),
                    User.name.label("owner_name")
                )
                .outerjoin(Contact, Lead.contact_id == Contact.id)
                .outerjoin(User, Lead.owner_id == User.id)
                .filter(Lead.organization_id == current_user.organization_id)
                .all()
            )
            logger.info(f"Found {len(leads)} leads for organization {current_user.organization_id}")
            # Convert to list of dicts for Pydantic
            result = [dict(lead._mapping) for lead in leads]
        except Exception as join_error:
            logger.warning(f"Join query failed: {join_error}")
            # Fallback to simple lead query
            leads = db.query(Lead).filter(Lead.organization_id == current_user.organization_id).all()
            result = [
                {
                    "id": lead.id,
                    "title": lead.title,
                    "status": lead.status,
                    "source": lead.source,
                    "created_at": lead.created_at,
                    "score": lead.score,
                    "score_updated_at": lead.score_updated_at,
                    "score_factors": lead.score_factors,
                    "score_confidence": lead.score_confidence,
                    "contact_name": None,
                    "company": None,
                    "owner_name": None
                }
                for lead in leads
            ]
        db.close()
        return result
    except Exception as e:
        logger.error(f"Database error in get_leads: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leads: {str(e)}")

@app.get("/api/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int):
    db: Session = get_session_local()()
    lead = (
        db.query(
            Lead.id,
            Lead.title,
            Lead.status,
            Lead.source,
            Lead.created_at,
            Contact.name.label("contact_name"),
            Contact.company.label("company"),
            User.name.label("owner_name")
        )
        .join(Contact, Lead.contact_id == Contact.id)
        .join(User, Lead.owner_id == User.id)
        .filter(Lead.id == lead_id)
        .first()
    )
    db.close()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return dict(lead._mapping)

@app.put("/api/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, update: LeadUpdate):
    db: Session = get_session_local()()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        db.close()
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    # Return with joined info
    result = (
        db.query(
            Lead.id,
            Lead.title,
            Lead.status,
            Lead.source,
            Lead.created_at,
            Contact.name.label("contact_name"),
            Contact.company.label("company"),
            User.name.label("owner_name")
        )
        .join(Contact, Lead.contact_id == Contact.id)
        .join(User, Lead.owner_id == User.id)
        .filter(Lead.id == lead_id)
        .first()
    )
    db.close()
    return dict(result._mapping)

@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: int):
    db: Session = get_session_local()()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        db.close()
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    db.close()
    return {"detail": "Lead deleted"}

# GET /api/contacts endpoint
@app.get("/api/contacts", response_model=list[ContactOut])
def get_contacts(current_user: User = Depends(get_current_user)):
    try:
        db: Session = get_session_local()()
        contacts = db.query(Contact).filter(Contact.organization_id == current_user.organization_id).all()
        
        result = []
        for contact in contacts:
            # Get owner name if exists
            owner_name = None
            if contact.owner_id:
                user = db.query(User).filter(User.id == contact.owner_id).first()
                if user:
                    owner_name = user.name
            
            result.append({
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "created_at": contact.created_at,
                "owner_name": owner_name
            })
        
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Database error in get_contacts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch contacts: {str(e)}")

# GET /api/contacts/{contact_id} endpoint
@app.get("/api/contacts/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int):
    db: Session = get_session_local()()
    contact = (
        db.query(
            Contact.id,
            Contact.name,
            Contact.email,
            Contact.phone,
            Contact.company,
            Contact.created_at,
            User.name.label("owner_name")
        )
        .join(User, Contact.owner_id == User.id, isouter=True)
        .filter(Contact.id == contact_id)
        .first()
    )
    db.close()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return dict(contact._mapping)

# PUT /api/contacts/{contact_id} endpoint
@app.put("/api/contacts/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, update: ContactUpdate):
    db: Session = get_session_local()()
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        db.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    # Return with joined info
    result = (
        db.query(
            Contact.id,
            Contact.name,
            Contact.email,
            Contact.phone,
            Contact.company,
            Contact.created_at,
            User.name.label("owner_name")
        )
        .join(User, Contact.owner_id == User.id, isouter=True)
        .filter(Contact.id == contact_id)
        .first()
    )
    db.close()
    return dict(result._mapping)

# POST /api/contacts endpoint (create new contact)
@app.post("/api/contacts", response_model=ContactOut)
def create_contact(contact_data: ContactUpdate, current_user: User = Depends(get_current_user)):
    try:
        db: Session = get_session_local()()
        
        # Create new contact
        new_contact = Contact(
            name=contact_data.name,
            email=contact_data.email,
            phone=contact_data.phone,
            company=contact_data.company,
            owner_id=current_user.id,  # Set to current user
            organization_id=current_user.organization_id  # Set to current user's organization
        )
        
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        
        # Get owner name for response
        owner_name = None
        if new_contact.owner_id:
            user = db.query(User).filter(User.id == new_contact.owner_id).first()
            if user:
                owner_name = user.name
        
        result = {
            "id": new_contact.id,
            "name": new_contact.name,
            "email": new_contact.email,
            "phone": new_contact.phone,
            "company": new_contact.company,
            "created_at": new_contact.created_at,
            "owner_name": owner_name
        }
        
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Database error in create_contact: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create contact: {str(e)}")

# DELETE /api/contacts/{contact_id} endpoint
@app.delete("/api/contacts/{contact_id}")
def delete_contact(contact_id: int):
    db: Session = get_session_local()()
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        db.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    db.close()
    return {"detail": "Contact deleted"}

# Catch-all route for frontend (MUST BE LAST!)
# Temporarily disabled to test API routes
# if os.path.exists(frontend_dist_path):
#     @app.get("/{path:path}")
#     async def serve_frontend(path: str):
#         """Serve the React frontend for all non-API routes"""
#         # Don't serve API routes - check if path starts with api/
#         if path.startswith("api/"):
#             raise HTTPException(status_code=404, detail="API endpoint not found")
#         
#         # Serve static files if they exist
#         static_file_path = os.path.join(frontend_dist_path, path)
#         if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
#             return FileResponse(static_file_path)
#         
#         # Serve index.html for all other routes (React Router)
#         index_path = os.path.join(frontend_dist_path, "index.html")
#         if os.path.exists(index_path):
#             return FileResponse(index_path)
#         else:
#             raise HTTPException(status_code=404, detail="Frontend not found")

