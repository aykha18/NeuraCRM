from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import json

# Create FastAPI app
app = FastAPI(
    title="CRM API",
    description="API for the CRM Application with AI Features",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "https://*.railway.app",
        "https://*.up.railway.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
leads_db = [
    {
        "id": 1,
        "title": "Sample Lead",
        "status": "New",
        "source": "Website",
        "created_at": datetime.now().isoformat(),
        "contact_name": "John Doe",
        "company": "Sample Corp",
        "owner_name": "Sales Team"
    }
]

contacts_db = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Sample Corp",
        "created_at": datetime.now().isoformat()
    }
]

next_lead_id = 2
next_contact_id = 2

@app.get("/")
def read_root():
    return {"message": "CRM API is running.", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.get("/api/test")
def test_api():
    return {"message": "API is working", "endpoints": ["/api/leads", "/api/contacts", "/api/leads/scoring-analytics"]}

# Leads endpoints
@app.get("/api/leads")
def get_leads():
    return leads_db

@app.post("/api/leads")
def create_lead(lead: dict):
    global next_lead_id
    new_lead = {
        "id": next_lead_id,
        "title": lead.get("title", "New Lead"),
        "status": lead.get("status", "New"),
        "source": lead.get("source", "Manual"),
        "created_at": datetime.now().isoformat(),
        "contact_name": lead.get("contact_name", ""),
        "company": lead.get("company", ""),
        "owner_name": lead.get("owner_name", "Sales Team")
    }
    leads_db.append(new_lead)
    next_lead_id += 1
    return new_lead

@app.put("/api/leads/{lead_id}")
def update_lead(lead_id: int, lead: dict):
    for i, existing_lead in enumerate(leads_db):
        if existing_lead["id"] == lead_id:
            leads_db[i].update(lead)
            leads_db[i]["id"] = lead_id  # Ensure ID doesn't change
            return leads_db[i]
    raise HTTPException(status_code=404, detail="Lead not found")

@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: int):
    for i, lead in enumerate(leads_db):
        if lead["id"] == lead_id:
            deleted_lead = leads_db.pop(i)
            return {"message": "Lead deleted successfully", "lead": deleted_lead}
    raise HTTPException(status_code=404, detail="Lead not found")

# Contacts endpoints
@app.get("/api/contacts")
def get_contacts():
    return contacts_db

@app.post("/api/contacts")
def create_contact(contact: dict):
    global next_contact_id
    new_contact = {
        "id": next_contact_id,
        "name": contact.get("name", "New Contact"),
        "email": contact.get("email", ""),
        "company": contact.get("company", ""),
        "created_at": datetime.now().isoformat()
    }
    contacts_db.append(new_contact)
    next_contact_id += 1
    return new_contact

@app.put("/api/contacts/{contact_id}")
def update_contact(contact_id: int, contact: dict):
    for i, existing_contact in enumerate(contacts_db):
        if existing_contact["id"] == contact_id:
            contacts_db[i].update(contact)
            contacts_db[i]["id"] = contact_id  # Ensure ID doesn't change
            return contacts_db[i]
    raise HTTPException(status_code=404, detail="Contact not found")

@app.delete("/api/contacts/{contact_id}")
def delete_contact(contact_id: int):
    for i, contact in enumerate(contacts_db):
        if contact["id"] == contact_id:
            deleted_contact = contacts_db.pop(i)
            return {"message": "Contact deleted successfully", "contact": deleted_contact}
    raise HTTPException(status_code=404, detail="Contact not found")

@app.get("/api/leads/scoring-analytics")
def get_scoring_analytics():
    return {
        "total_leads": len(leads_db),
        "average_score": 75,
        "score_distribution": {
            "high": len(leads_db),
            "medium": 0,
            "low": 0
        }
    }

@app.get("/api/db-test")
def test_database():
    """Test database connection"""
    try:
        from api.db import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            return {"status": "success", "message": "Database connected!", "result": result.fetchone()[0]}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}

@app.get("/api/db-url")
def get_database_url():
    """Get database URL (masked)"""
    import os
    db_url = os.getenv("DATABASE_URL", "Not set")
    if db_url != "Not set":
        # Mask the password in the URL
        if "@" in db_url:
            parts = db_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                if len(user_pass) >= 3:
                    user_pass[2] = "***"
                    parts[0] = ":".join(user_pass)
                    db_url = "@".join(parts)
    return {"database_url": db_url}
