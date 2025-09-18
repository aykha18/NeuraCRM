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
load_dotenv()

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
        
        # Get user's organization to show organization-wide data if user has no deals
        user_org_id = user.organization_id if user else None
        
        # Get deals data - first try user's deals, then organization deals if none
        user_deals_count = db.query(Deal).filter(Deal.owner_id == user_id).count()
        if user_deals_count == 0 and user_org_id:
            # User has no deals, show organization deals
            deals_count = db.query(Deal).filter(Deal.organization_id == user_org_id).count()
            total_value = db.query(func.sum(Deal.value)).filter(Deal.organization_id == user_org_id).scalar() or 0
            open_deals = db.query(Deal).filter(Deal.organization_id == user_org_id, Deal.status == 'open').count()
            won_deals = db.query(Deal).filter(Deal.organization_id == user_org_id, Deal.status == 'won').count()
            top_deals = db.query(Deal).filter(Deal.organization_id == user_org_id).order_by(Deal.value.desc()).limit(8).all()
        else:
            # User has deals, use user-specific data
            deals_count = user_deals_count
            total_value = db.query(func.sum(Deal.value)).filter(Deal.owner_id == user_id).scalar() or 0
            open_deals = db.query(Deal).filter(Deal.owner_id == user_id, Deal.status == 'open').count()
            won_deals = db.query(Deal).filter(Deal.owner_id == user_id, Deal.status == 'won').count()
            top_deals = db.query(Deal).filter(Deal.owner_id == user_id).order_by(Deal.value.desc()).limit(8).all()
        deals_info = []
        for deal in top_deals:
            # Calculate probability based on stage
            probability = 0
            if deal.status == 'won':
                probability = 100
            elif deal.status == 'lost':
                probability = 0
            elif deal.stage:
                stage_probabilities = {
                    'prospecting': 10, 'qualification': 25, 'proposal': 50,
                    'negotiation': 75, 'closing': 90
                }
                probability = stage_probabilities.get(deal.stage.name.lower() if deal.stage else 'prospecting', 20)
            
            deals_info.append(f"- Deal #{deal.id}: {deal.title} (${deal.value or 0:,.0f}, {probability}% probability, {deal.status}, closes {deal.reminder_date.strftime('%Y-%m-%d') if deal.reminder_date else 'Not set'})")
        
        # Get comprehensive leads data - try user first, then organization
        user_leads_count = db.query(Lead).filter(Lead.owner_id == user_id).count()
        if user_leads_count == 0 and user_org_id:
            # User has no leads, show organization leads
            leads_count = db.query(Lead).filter(Lead.organization_id == user_org_id).count()
            hot_leads = db.query(Lead).filter(Lead.organization_id == user_org_id, Lead.score >= 70).count()
            top_leads = db.query(Lead).filter(Lead.organization_id == user_org_id).order_by(Lead.score.desc()).limit(5).all()
        else:
            # User has leads, use user-specific data
            leads_count = user_leads_count
            hot_leads = db.query(Lead).filter(Lead.owner_id == user_id, Lead.score >= 70).count()
            top_leads = db.query(Lead).filter(Lead.owner_id == user_id).order_by(Lead.score.desc()).limit(5).all()
        leads_info = []
        for lead in top_leads:
            leads_info.append(f"- Lead #{lead.id}: {lead.title} (Score: {lead.score}, Confidence: {lead.score_confidence or 0.0:.1f}, Source: {lead.source or 'Unknown'})")
        
        # Get contacts data - try user first, then organization
        user_contacts_count = db.query(Contact).filter(Contact.owner_id == user_id).count()
        if user_contacts_count == 0 and user_org_id:
            contacts_count = db.query(Contact).filter(Contact.organization_id == user_org_id).count()
        else:
            contacts_count = user_contacts_count
        
        # Get support data
        support_tickets_count = db.query(SupportTicket).count()
        open_support_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(['open', 'in_progress'])).count()
        knowledge_articles_count = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.status == 'published').count()
        
        # Determine data scope
        data_scope = "organization-wide" if (user_deals_count == 0 and user_org_id) else "user-specific"
        
        context = f"""
CRM Context for {user_name} (User ID: {user_id}) - Showing {data_scope} data:

📊 SALES PIPELINE:
- Total Deals: {deals_count} (${total_value:,.0f} total value)
- Open Deals: {open_deals}
- Won Deals: {won_deals}
- Total Leads: {leads_count} (Hot leads: {hot_leads})
- Total Contacts: {contacts_count}

🎯 TOP DEALS (by value & probability):
{chr(10).join(deals_info) if deals_info else "No deals found"}

🔥 HOT LEADS (score ≥70):
{chr(10).join(leads_info) if leads_info else "No hot leads"}

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
    
    # Optimized system prompt for data-driven responses
    system_prompt = f"""You are a data-driven AI Sales Assistant for NeuraCRM. You have access to {user_name}'s real CRM data and must provide specific, actionable insights.

## CRITICAL INSTRUCTIONS:
- ALWAYS analyze the actual CRM data provided
- Give SPECIFIC results, not generic advice
- Use REAL deal names, amounts, stages, and probabilities from the data
- Be concise and direct - no lengthy explanations unless requested
- Focus on immediate actionable insights

## Response Format:
- For deal analysis: List specific deals with names, amounts, and win probabilities
- For pipeline insights: Reference actual numbers and percentages
- For recommendations: Give specific next steps based on real data
- Use bullet points and clear formatting

## Example Response Style:
Instead of: "Look at deals in negotiation stage..."
Say: "Your top 2 deals likely to close:
1. Deal #123: ABC Corp ($50,000, 85% probability, closes 2024-02-15)
2. Deal #456: XYZ Inc ($35,000, 70% probability, closes 2024-02-28)"

Always base your response on the actual CRM data provided."""

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