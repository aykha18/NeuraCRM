from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import Deal, Contact, Lead, User
from sqlalchemy import func

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
)

class AIChatRequest(BaseModel):
    message: str
    user_id: int

class AIChatResponse(BaseModel):
    response: str

def get_crm_context(db: Session, user_id: int) -> str:
    """Fetch minimal CRM data to provide context for AI responses"""
    try:
        # Get only essential data to reduce query time
        deals_count = db.query(Deal).filter(Deal.owner_id == user_id).count()
        total_value = db.query(func.sum(Deal.value)).filter(Deal.owner_id == user_id).scalar() or 0
        
        # Get top 3 deals only
        top_deals = db.query(Deal).filter(Deal.owner_id == user_id).order_by(Deal.value.desc()).limit(3).all()
        deals_info = []
        for deal in top_deals:
            deals_info.append(f"- {deal.title}: ${deal.value or 0}")
        
        context = f"""
Quick CRM Summary for User {user_id}:
- Total deals: {deals_count}
- Total pipeline value: ${total_value:,.0f}
- Top deals: {chr(10).join(deals_info) if deals_info else "No deals found"}
"""
        return context
    except Exception as e:
        return f"CRM data unavailable: {str(e)}"

@router.post("/assistant", response_model=AIChatResponse)
def ai_assistant(request: AIChatRequest, db: Session = Depends(get_db)):
    # Fetch minimal CRM context
    crm_context = get_crm_context(db, request.user_id)

    # Simplified prompt for faster response
    system_prompt = f"""You are a helpful AI Sales Assistant. Keep responses brief and conversational.

CRM Context: {crm_context}

Respond naturally and helpfully to sales questions."""

    # Shorter, more direct prompt
    prompt = f"{system_prompt}\n\nUser: {request.message}\nAssistant:"

    # Call local Ollama API with shorter timeout
    try:
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3",
                "prompt": prompt,
                "stream": False
            },
            timeout=15  # Reduced timeout to 15 seconds
        )
        ollama_response.raise_for_status()
        data = ollama_response.json()
        ai_text = data.get("response", "I'm having trouble connecting right now. Please try again.")
        
        # Clean up the response
        ai_text = ai_text.strip()
        if ai_text.startswith("Assistant:"):
            ai_text = ai_text[10:].strip()
        
        # Ensure we have a response
        if not ai_text or len(ai_text) < 10:
            ai_text = "I'm sorry, I couldn't generate a proper response. Please try asking your question again."
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="AI response timed out. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    return AIChatResponse(response=ai_text) 