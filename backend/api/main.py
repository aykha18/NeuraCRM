from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

# Import routers
from api.routers import kanban
from api.routers.dashboard import router as dashboard_router
from api.routers.ai import router as ai_router

# Import database and models
from api.db import SessionLocal
from api.models import Lead, Contact, User

# Import Pydantic models
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="CRM API",
    description="API for the CRM Application with AI Features",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. For prod, use your frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(kanban.router)
app.include_router(dashboard_router)
app.include_router(ai_router)

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
    class Config:
        orm_mode = True

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
        orm_mode = True

# Pydantic schema for Contact updates
class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    owner_id: int | None = None

@app.get("/")
def read_root():
    return {"message": "CRM API is running."}

@app.post("/chat/")
def chat_with_ai(message: Message):
    # This would call OpenAI or local LLM in real usage
    return {"response": f"AI response to: '{message.content}' from {message.user}"}

# GET /api/leads endpoint (with joins)
@app.get("/api/leads", response_model=list[LeadOut])
def get_leads():
    db: Session = SessionLocal()
    leads = (
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
        .all()
    )
    db.close()
    # Convert to list of dicts for Pydantic
    return [dict(lead._mapping) for lead in leads]

@app.get("/api/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int):
    db: Session = SessionLocal()
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
    db: Session = SessionLocal()
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
    db: Session = SessionLocal()
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
    db: Session = SessionLocal()
    contacts = (
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
        .all()
    )
    db.close()
    # Convert to list of dicts for Pydantic
    return [dict(contact._mapping) for contact in contacts]

# GET /api/contacts/{contact_id} endpoint
@app.get("/api/contacts/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int):
    db: Session = SessionLocal()
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
    db: Session = SessionLocal()
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

# DELETE /api/contacts/{contact_id} endpoint
@app.delete("/api/contacts/{contact_id}")
def delete_contact(contact_id: int):
    db: Session = SessionLocal()
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        db.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    db.close()
    return {"detail": "Contact deleted"}
