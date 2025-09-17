from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI
from api.db import get_db
from api.models import Deal, Contact, Lead, User
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=".env")

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

    # System prompt for GPT models
    system_prompt = (
        "You are a helpful AI Sales Assistant for a CRM. Be concise, specific, and actionable.\n"
        "Use the provided CRM context to ground your answers. If information is missing, ask a short clarifying question."
    )

    # Compose messages for OpenAI
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\nCRM Context:\n{crm_context}"},
        {"role": "user", "content": request.message},
    ]

    try:
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not found in environment variables")
        
        client = OpenAI(api_key=api_key)  # explicitly pass API key
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.5,
        )
        ai_text = completion.choices[0].message.content or ""
        ai_text = ai_text.strip()
        if not ai_text:
            ai_text = "I'm sorry, I couldn't generate a response just now. Please try again."
        return AIChatResponse(response=ai_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")