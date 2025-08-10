from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
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

@app.get("/")
def read_root():
    return {"message": "CRM API is running.", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.get("/api/test")
def test_api():
    return {"message": "API is working", "endpoints": ["/api/leads", "/api/contacts", "/api/leads/scoring-analytics"]}

@app.get("/api/leads")
def get_leads():
    # Return sample data for now
    return [
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

@app.get("/api/contacts")
def get_contacts():
    # Return sample data for now
    return [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "company": "Sample Corp",
            "created_at": datetime.now().isoformat()
        }
    ]

@app.get("/api/leads/scoring-analytics")
def get_scoring_analytics():
    return {
        "total_leads": 1,
        "average_score": 75,
        "score_distribution": {
            "high": 1,
            "medium": 0,
            "low": 0
        }
    }
