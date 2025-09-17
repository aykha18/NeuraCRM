"""
Enhanced AI Router with Comprehensive Sales Assistant Integration
Provides advanced AI capabilities with full CRM data access and email automation
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime

from api.db import get_db
from api.dependencies import get_current_user
from api.models import User
from ai.sales_assistant_optimized import OptimizedSalesAssistant
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.base import AIModel

router = APIRouter(prefix="/api/ai-enhanced", tags=["AI Enhanced"])

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to the AI assistant")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=None, description="Previous conversation messages")
    include_insights: bool = Field(default=False, description="Include sales insights in response")

class ChatResponse(BaseModel):
    response: str
    function_calls: List[Dict[str, Any]] = []
    insights: Optional[Dict[str, Any]] = None
    model: str
    usage: Optional[Dict[str, Any]] = None
    timestamp: str

class InsightsRequest(BaseModel):
    entity_type: Optional[str] = Field(default=None, description="Type of entity to analyze (lead, deal, contact)")
    entity_id: Optional[int] = Field(default=None, description="ID of specific entity to analyze")

class EmailGenerationRequest(BaseModel):
    template_id: int = Field(..., description="ID of email template to use")
    recipient_id: int = Field(..., description="ID of recipient (contact/lead/deal)")
    recipient_type: str = Field(..., description="Type of recipient (contact, lead, deal)")
    custom_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for personalization")
    send_immediately: bool = Field(default=False, description="Send email immediately after generation")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    entity_types: List[str] = Field(default=["contacts", "leads", "deals"], description="Types of entities to search")

@router.post("/chat", response_model=ChatResponse)
async def enhanced_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced chat with AI sales assistant
    Provides comprehensive CRM assistance with function calling
    """
    try:
        # Initialize sales assistant
        assistant = OptimizedSalesAssistant(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        # Process message
        result = await assistant.process_message(
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        # Add insights if requested
        insights = None
        if request.include_insights:
            insights = await assistant.generate_sales_insights()
        
        return ChatResponse(
            response=result["response"],
            function_calls=result["function_calls"],
            insights=insights,
            model=result["model"],
            usage=result["usage"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

@router.post("/insights")
async def get_sales_insights(
    request: InsightsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive sales insights
    Can analyze specific entities or provide general insights
    """
    try:
        assistant = OptimizedSalesAssistant(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        if request.entity_type and request.entity_id:
            # Get insights for specific entity
            insights = await assistant.suggest_next_actions(
                entity_type=request.entity_type,
                entity_id=request.entity_id
            )
        else:
            # Get general sales insights
            insights = await assistant.generate_sales_insights()
        
        return {
            "success": True,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation error: {str(e)}")

@router.post("/generate-email")
async def generate_personalized_email(
    request: EmailGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized email using AI and templates
    Optionally send immediately
    """
    try:
        assistant = OptimizedSalesAssistant(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        # Generate email using function
        function_call = {
            "name": "generate_email",
            "arguments": {
                "template_id": request.template_id,
                "recipient_id": request.recipient_id,
                "recipient_type": request.recipient_type,
                "custom_context": request.custom_context or {}
            }
        }
        
        result = await assistant._execute_function(function_call)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Email generation failed"))
        
        email_data = result["result"]
        
        # Send email if requested
        if request.send_immediately:
            # Add background task to send email
            background_tasks.add_task(
                _send_email_task,
                email_data,
                current_user.id,
                db
            )
        
        return {
            "success": True,
            "email": email_data,
            "sent": request.send_immediately,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email generation error: {str(e)}")

@router.post("/search")
async def search_crm(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search across CRM entities with AI assistance
    """
    try:
        assistant = OptimizedSalesAssistant(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        # Use data access layer for search
        results = assistant.data_access.search_entities(
            query=request.query,
            entity_types=request.entity_types
        )
        
        # Enhance results with AI insights
        if results:
            search_prompt = f"""Based on this search for "{request.query}", provide insights:

Results: {results}

Provide:
1. Key patterns or insights
2. Recommended next actions
3. Priority contacts/deals to focus on
4. Potential opportunities"""

            messages = [
                {"role": "system", "content": "You are a sales intelligence expert. Analyze search results and provide actionable insights."},
                {"role": "user", "content": search_prompt}
            ]
            
            # Get AI insights
            ai_response = await assistant.provider.chat_completion(
                messages=[assistant.provider._convert_message(msg) for msg in messages],
                temperature=0.3
            )
            
            insights = ai_response.content
        else:
            insights = "No results found. Consider expanding your search terms or checking different entity types."
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "insights": insights,
            "total_results": sum(len(entity_results) for entity_results in results.values()),
            "searched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/templates")
async def get_email_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available email templates
    """
    try:
        assistant = OptimizedSalesAssistant(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        templates = assistant.data_access.get_email_templates(category)
        
        return {
            "success": True,
            "templates": templates,
            "category": category,
            "total": len(templates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template retrieval error: {str(e)}")

@router.get("/pipeline-analysis")
async def get_pipeline_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive pipeline analysis with AI insights
    """
    try:
        assistant = OptimizedSalesAssistant(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        # Get pipeline data
        pipeline_data = assistant.data_access.get_pipeline_summary()
        
        # Generate AI analysis
        analysis_prompt = f"""Analyze this sales pipeline and provide insights:

Pipeline Data: {pipeline_data}

Provide:
1. Pipeline health assessment
2. Bottlenecks and opportunities
3. Stage-specific recommendations
4. Revenue forecasting insights
5. Action items for improvement"""

        messages = [
            {"role": "system", "content": "You are a sales pipeline expert. Analyze pipeline data and provide strategic insights."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        ai_response = await assistant.provider.chat_completion(
            messages=[assistant.provider._convert_message(msg) for msg in messages],
            temperature=0.3
        )
        
        return {
            "success": True,
            "pipeline_data": pipeline_data,
            "ai_analysis": ai_response.content,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline analysis error: {str(e)}")

@router.get("/model-info")
async def get_model_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the current AI model
    """
    try:
        provider = OpenAIProvider(model=AIModel.GPT_4O_MINI)
        model_info = provider.get_model_info()
        
        return {
            "success": True,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model info error: {str(e)}")

# Background task functions
async def _send_email_task(email_data: Dict[str, Any], user_id: int, db: Session):
    """Background task to send email"""
    try:
        # Here you would integrate with your email service (SendGrid, AWS SES, etc.)
        # For now, we'll just log the email
        print(f"Email would be sent: {email_data['subject']} to {email_data['recipient']['email']}")
        
        # You could also create an EmailLog entry here
        # from api.models import EmailLog
        # email_log = EmailLog(...)
        # db.add(email_log)
        # db.commit()
        
    except Exception as e:
        print(f"Email sending failed: {str(e)}")

# Helper method for message conversion
def _convert_message(self, msg: Dict[str, str]):
    """Convert dict message to AIMessage"""
    from ai.providers.base import AIMessage
    return AIMessage(role=msg["role"], content=msg["content"])

# Add the helper method to the provider
OpenAIProvider._convert_message = _convert_message
