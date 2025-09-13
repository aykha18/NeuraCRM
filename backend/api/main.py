from fastapi import FastAPI, Depends, HTTPException
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database and models first
from api.db import get_session_local, get_engine
from api.models import Lead, Contact, User, Base

# Import Pydantic models
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="CRM API",
    description="API for the CRM Application with AI Features",
    version="1.0.0"
)

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
        
        # Import routers after database is ready
        try:
            from api.routers import kanban
            from api.routers.dashboard import router as dashboard_router
            from api.routers.ai import router as ai_router
            from api.routers.email_automation import router as email_automation_router
            from api.lead_scoring import lead_scoring_service
            
            # Include routers
            app.include_router(kanban.router)
            app.include_router(dashboard_router)
            app.include_router(ai_router)
            app.include_router(email_automation_router)
            
            logger.info("All routers loaded successfully!")
            
        except Exception as e:
            logger.warning(f"Some routers failed to load: {e}")
            # Continue without the problematic routers
        
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
        "https://neuracrm.up.railway.app",  # Your Railway backend
        "https://*.railway.app",  # Allow Railway domains
        "https://*.up.railway.app",  # Allow Railway domains
        "*"  # Allow all origins in production (you can restrict this later)
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
    app.mount("/static", StaticFiles(directory=frontend_dist_path), name="static")
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

@app.get("/")
def read_root():
    """Serve the frontend index.html at root"""
    if os.path.exists(frontend_dist_path):
        index_path = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # Fallback to JSON if frontend not available
    return {"message": "CRM API is running.", "status": "healthy"}

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
def create_lead(lead_data: LeadUpdate):
    db: Session = get_session_local()()
    
    try:
        # Create new lead
        new_lead = Lead(
            title=lead_data.title,
            status=lead_data.status or "new",
            source=lead_data.source or "manual",
            contact_id=lead_data.contact_id or 1,  # Default to contact 1
            owner_id=lead_data.owner_id or 1,  # Default to user 1
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

# GET /api/leads endpoint (with joins)
@app.get("/api/leads", response_model=list[LeadOut])
def get_leads():
    try:
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
                .all()
            )
            # Convert to list of dicts for Pydantic
            result = [dict(lead._mapping) for lead in leads]
        except Exception as join_error:
            logger.warning(f"Join query failed: {join_error}")
            # Fallback to simple lead query
            leads = db.query(Lead).all()
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
def get_contacts():
    try:
        db: Session = get_session_local()()
        contacts = db.query(Contact).all()
        
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
def create_contact(contact_data: ContactUpdate):
    try:
        db: Session = get_session_local()()
        
        # Create new contact
        new_contact = Contact(
            name=contact_data.name,
            email=contact_data.email,
            phone=contact_data.phone,
            company=contact_data.company,
            owner_id=1  # Default owner - you might want to get this from auth
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
if os.path.exists(frontend_dist_path):
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve the React frontend for all non-API routes"""
        # Don't serve API routes
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve static files if they exist
        static_file_path = os.path.join(frontend_dist_path, path)
        if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
            return FileResponse(static_file_path)
        
        # Serve index.html for all other routes (React Router)
        index_path = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")

