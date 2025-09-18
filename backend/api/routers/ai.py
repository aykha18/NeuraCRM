from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI
from api.db import get_db
from api.models import Deal, Contact, Lead, User, SupportTicket, KnowledgeBaseArticle
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="../.env")

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
    """Fetch comprehensive CRM data to provide context for AI responses"""
    try:
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.name if user else "User"
        
        # Get deals data
        deals_count = db.query(Deal).filter(Deal.owner_id == user_id).count()
        total_value = db.query(func.sum(Deal.value)).filter(Deal.owner_id == user_id).scalar() or 0
        open_deals = db.query(Deal).filter(Deal.owner_id == user_id, Deal.status == 'open').count()
        won_deals = db.query(Deal).filter(Deal.owner_id == user_id, Deal.status == 'won').count()
        
        # Get top 5 deals with stages
        top_deals = db.query(Deal).filter(Deal.owner_id == user_id).order_by(Deal.value.desc()).limit(5).all()
        deals_info = []
        for deal in top_deals:
            deals_info.append(f"- {deal.title}: ${deal.value or 0} ({deal.status})")
        
        # Get leads data
        leads_count = db.query(Lead).filter(Lead.owner_id == user_id).count()
        hot_leads = db.query(Lead).filter(Lead.owner_id == user_id, Lead.status == 'hot').count()
        
        # Get contacts data
        contacts_count = db.query(Contact).filter(Contact.owner_id == user_id).count()
        
        # Get support data
        support_tickets_count = db.query(SupportTicket).count()
        open_support_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(['open', 'in_progress'])).count()
        knowledge_articles_count = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.status == 'published').count()
        
        context = f"""
CRM Context for {user_name} (User ID: {user_id}):

📊 SALES PIPELINE:
- Total Deals: {deals_count} (${total_value:,.0f} total value)
- Open Deals: {open_deals}
- Won Deals: {won_deals}
- Total Leads: {leads_count} (Hot leads: {hot_leads})
- Total Contacts: {contacts_count}

🎯 TOP DEALS:
{chr(10).join(deals_info) if deals_info else "No deals found"}

🛠️ CUSTOMER SUPPORT:
- Total Support Tickets: {support_tickets_count}
- Open Support Tickets: {open_support_tickets}
- Knowledge Base Articles: {knowledge_articles_count}

💡 SALES INSIGHTS:
- Pipeline Health: {'Strong' if deals_count > 10 else 'Growing' if deals_count > 5 else 'Early Stage'}
- Average Deal Size: ${(total_value / deals_count):,.0f} if deals_count > 0 else 'No data'
- Conversion Rate: {(won_deals / deals_count * 100):.1f}% if deals_count > 0 else 'No data'
- Support Load: {'High' if open_support_tickets > 20 else 'Moderate' if open_support_tickets > 10 else 'Low'}
"""
        return context
    except Exception as e:
        return f"CRM data unavailable: {str(e)}"

@router.post("/assistant", response_model=AIChatResponse)
def ai_assistant(request: AIChatRequest, db: Session = Depends(get_db)):
    # Fetch minimal CRM context
    crm_context = get_crm_context(db, request.user_id)

    # Get user info for personalized responses
    user = db.query(User).filter(User.id == request.user_id).first()
    user_name = user.name if user else "User"
    
    # Enhanced system prompt for GPT models
    system_prompt = f"""You are an advanced AI Sales Assistant for NeuraCRM, helping {user_name} with their sales activities.

## Your Expertise:
- Lead qualification and scoring
- Deal progression and pipeline management  
- Sales strategy and tactics
- Customer relationship management
- Revenue optimization

## Your Approach:
1. **Data-Driven**: Always reference specific CRM data when available
2. **Actionable**: Provide concrete next steps and recommendations
3. **Personalized**: Tailor responses to {user_name}'s specific situation
4. **Strategic**: Think beyond immediate tasks to long-term success
5. **Proactive**: Identify opportunities and suggest improvements

## Response Style:
- Be conversational but professional
- Use specific examples from their CRM data
- Provide numbered lists for action items
- Ask clarifying questions when needed
- Focus on high-impact activities

## Key Areas to Help With:
- Pipeline analysis and optimization
- Lead scoring and qualification
- Deal strategy and progression
- Follow-up recommendations
- Revenue forecasting
- Customer relationship building
- Customer support and service
- Knowledge base article suggestions
- Support ticket analysis and recommendations

Always ground your responses in the provided CRM context. If data is missing, ask specific questions to gather more information."""

    # Compose messages for OpenAI
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\nCRM Context:\n{crm_context}"},
        {"role": "user", "content": request.message},
    ]

    try:
        # Get API key from environment (handle BOM issues)
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("\ufeffOPENAI_API_KEY")
        if not api_key:
            # Debug: Check what environment variables are available
            env_debug = {k: v[:10] + "..." if len(v) > 10 else v for k, v in os.environ.items() if 'OPENAI' in k.upper()}
            raise HTTPException(status_code=500, detail=f"OpenAI API key not found in environment variables. Available OPENAI vars: {env_debug}")
        
        client = OpenAI(api_key=api_key)  # explicitly pass API key
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.7,
        )
        ai_text = completion.choices[0].message.content or ""
        ai_text = ai_text.strip()
        if not ai_text:
            ai_text = "I'm sorry, I couldn't generate a response just now. Please try again."
        return AIChatResponse(response=ai_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")