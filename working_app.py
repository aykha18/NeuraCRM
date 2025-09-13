#!/usr/bin/env python3
"""
Working CRM App - Actually serves the frontend
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

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
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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
