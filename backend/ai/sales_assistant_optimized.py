"""
Optimized AI Sales Assistant with Comprehensive CRM Integration
Provides intelligent sales assistance with full data access and email automation
"""
import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from .providers.base import BaseAIProvider, AIModel, AIMessage
from .providers.openai_provider import OpenAIProvider
from .data_access import CRMDataAccess
from api.models import User, Lead, Deal, Contact, EmailTemplate, EmailCampaign
from api.email_automation import email_automation_service

class OptimizedSalesAssistant:
    """Advanced AI Sales Assistant with full CRM integration"""
    
    def __init__(self, db: Session, user_id: int, organization_id: int, provider: BaseAIProvider = None):
        self.db = db
        self.user_id = user_id
        self.organization_id = organization_id
        self.data_access = CRMDataAccess(db, user_id, organization_id)
        
        # Initialize AI provider
        if provider is None:
            self.provider = OpenAIProvider(model=AIModel.GPT_4O_MINI)
        else:
            self.provider = provider
        
        # Define available functions for the AI
        self.functions = self._define_functions()
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """Define available functions for the AI assistant"""
        return [
            {
                "name": "get_lead_details",
                "description": "Get comprehensive details about a specific lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "integer", "description": "ID of the lead to get details for"}
                    },
                    "required": ["lead_id"]
                }
            },
            {
                "name": "get_deal_details",
                "description": "Get comprehensive details about a specific deal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "integer", "description": "ID of the deal to get details for"}
                    },
                    "required": ["deal_id"]
                }
            },
            {
                "name": "get_contact_details",
                "description": "Get comprehensive details about a specific contact",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_id": {"type": "integer", "description": "ID of the contact to get details for"}
                    },
                    "required": ["contact_id"]
                }
            },
            {
                "name": "search_crm",
                "description": "Search across contacts, leads, and deals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "entity_types": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["contacts", "leads", "deals"]},
                            "description": "Types of entities to search"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "generate_email",
                "description": "Generate a personalized email for a contact, lead, or deal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "integer", "description": "ID of the email template to use"},
                        "recipient_id": {"type": "integer", "description": "ID of the recipient (contact/lead/deal)"},
                        "recipient_type": {"type": "string", "enum": ["contact", "lead", "deal"], "description": "Type of recipient"},
                        "custom_context": {"type": "object", "description": "Additional context for personalization"}
                    },
                    "required": ["template_id", "recipient_id", "recipient_type"]
                }
            },
            {
                "name": "analyze_pipeline",
                "description": "Get pipeline analysis and insights",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_email_templates",
                "description": "Get available email templates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Filter by template category"}
                    },
                    "required": []
                }
            },
            {
                "name": "schedule_follow_up",
                "description": "Schedule a follow-up activity for a deal or lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"type": "integer", "description": "ID of the deal or lead"},
                        "entity_type": {"type": "string", "enum": ["deal", "lead"], "description": "Type of entity"},
                        "follow_up_date": {"type": "string", "description": "Date for follow-up (ISO format)"},
                        "notes": {"type": "string", "description": "Notes for the follow-up"}
                    },
                    "required": ["entity_id", "entity_type", "follow_up_date"]
                }
            }
        ]
    
    async def process_message(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Process a user message and return AI response with actions"""
        
        # Build conversation context
        messages = self._build_conversation_context(message, conversation_history)
        
        # Get AI response with function calling
        response = await self.provider.chat_completion(
            messages=messages,
            functions=self.functions,
            function_call="auto",
            temperature=0.7
        )
        
        # Process function calls if any
        function_results = []
        if response.function_calls:
            for function_call in response.function_calls:
                result = await self._execute_function(function_call)
                function_results.append(result)
        
        # Generate final response
        final_response = await self._generate_final_response(
            messages, response, function_results
        )
        
        return {
            "response": final_response,
            "function_calls": function_results,
            "model": response.model,
            "usage": response.usage,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_conversation_context(self, message: str, history: List[Dict[str, str]] = None) -> List[AIMessage]:
        """Build conversation context with system prompt and history"""
        
        # Get comprehensive context
        user_context = self.data_access.get_user_context()
        org_context = self.data_access.get_organization_context()
        
        system_prompt = f"""You are an advanced AI Sales Assistant for {org_context.get('organization', {}).get('name', 'the organization')}.

## Your Role
You are a knowledgeable sales assistant that helps sales professionals with:
- Lead and deal management
- Email generation and automation
- Pipeline analysis and insights
- Contact relationship management
- Sales strategy and recommendations

## Available Data
- User: {user_context.get('user', {}).get('name', 'Unknown')} ({user_context.get('user', {}).get('role', 'sales')})
- Organization: {org_context.get('organization', {}).get('name', 'Unknown')}
- Performance: {user_context.get('performance', {})}
- Pipeline: {org_context.get('metrics', {})}

## Guidelines
1. Be proactive and helpful - suggest actions and insights
2. Use available functions to get detailed information when needed
3. Provide specific, actionable recommendations
4. Always consider the user's role and organization context
5. Generate personalized emails when appropriate
6. Analyze data to provide insights and recommendations

## Response Style
- Professional but conversational
- Data-driven insights
- Actionable recommendations
- Clear next steps

You have access to comprehensive CRM data and can perform various actions. Use the available functions to gather information and provide the best assistance possible."""

        messages = [AIMessage(role="system", content=system_prompt)]
        
        # Add conversation history
        if history:
            for msg in history[-10:]:  # Keep last 10 messages for context
                messages.append(AIMessage(role=msg.get("role", "user"), content=msg.get("content", "")))
        
        # Add current message
        messages.append(AIMessage(role="user", content=message))
        
        return messages
    
    async def _execute_function(self, function_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call and return results"""
        function_name = function_call["name"]
        arguments = function_call["arguments"]
        
        try:
            if function_name == "get_lead_details":
                lead_id = arguments["lead_id"]
                result = self.data_access.get_lead_context(lead_id)
                return {"function": function_name, "result": result, "success": True}
            
            elif function_name == "get_deal_details":
                deal_id = arguments["deal_id"]
                result = self.data_access.get_deal_context(deal_id)
                return {"function": function_name, "result": result, "success": True}
            
            elif function_name == "get_contact_details":
                contact_id = arguments["contact_id"]
                result = self.data_access.get_contact_context(contact_id)
                return {"function": function_name, "result": result, "success": True}
            
            elif function_name == "search_crm":
                query = arguments["query"]
                entity_types = arguments.get("entity_types", ["contacts", "leads", "deals"])
                result = self.data_access.search_entities(query, entity_types)
                return {"function": function_name, "result": result, "success": True}
            
            elif function_name == "generate_email":
                return await self._generate_email_function(arguments)
            
            elif function_name == "analyze_pipeline":
                result = self.data_access.get_pipeline_summary()
                return {"function": function_name, "result": result, "success": True}
            
            elif function_name == "get_email_templates":
                category = arguments.get("category")
                result = self.data_access.get_email_templates(category)
                return {"function": function_name, "result": result, "success": True}
            
            elif function_name == "schedule_follow_up":
                return await self._schedule_follow_up_function(arguments)
            
            else:
                return {"function": function_name, "error": "Unknown function", "success": False}
                
        except Exception as e:
            return {"function": function_name, "error": str(e), "success": False}
    
    async def _generate_email_function(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized email using template and context"""
        try:
            template_id = arguments["template_id"]
            recipient_id = arguments["recipient_id"]
            recipient_type = arguments["recipient_type"]
            custom_context = arguments.get("custom_context", {})
            
            # Get email template
            template = self.db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
            if not template:
                return {"function": "generate_email", "error": "Template not found", "success": False}
            
            # Get recipient context
            if recipient_type == "contact":
                context = self.data_access.get_contact_context(recipient_id)
            elif recipient_type == "lead":
                context = self.data_access.get_lead_context(recipient_id)
            elif recipient_type == "deal":
                context = self.data_access.get_deal_context(recipient_id)
            else:
                return {"function": "generate_email", "error": "Invalid recipient type", "success": False}
            
            # Merge custom context
            context.update(custom_context)
            
            # Generate personalized email
            personalized = email_automation_service.personalize_template(template, context)
            
            return {
                "function": "generate_email",
                "result": {
                    "subject": personalized["subject"],
                    "body": personalized["body"],
                    "recipient": context.get(recipient_type, {}),
                    "template": {
                        "id": template.id,
                        "name": template.name,
                        "category": template.category
                    }
                },
                "success": True
            }
            
        except Exception as e:
            return {"function": "generate_email", "error": str(e), "success": False}
    
    async def _schedule_follow_up_function(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a follow-up activity"""
        try:
            entity_id = arguments["entity_id"]
            entity_type = arguments["entity_type"]
            follow_up_date = arguments["follow_up_date"]
            notes = arguments.get("notes", "")
            
            # Create activity record
            from api.models import Activity
            activity = Activity(
                deal_id=entity_id if entity_type == "deal" else None,
                user_id=self.user_id,
                type="follow_up",
                message=f"Follow-up scheduled: {notes}",
                timestamp=datetime.fromisoformat(follow_up_date.replace('Z', '+00:00'))
            )
            
            self.db.add(activity)
            self.db.commit()
            
            return {
                "function": "schedule_follow_up",
                "result": {
                    "activity_id": activity.id,
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "follow_up_date": follow_up_date,
                    "notes": notes
                },
                "success": True
            }
            
        except Exception as e:
            return {"function": "schedule_follow_up", "error": str(e), "success": False}
    
    async def _generate_final_response(
        self, 
        messages: List[AIMessage], 
        ai_response: Any, 
        function_results: List[Dict[str, Any]]
    ) -> str:
        """Generate final response incorporating function results"""
        
        if not function_results:
            return ai_response.content
        
        # Add function results to conversation
        function_messages = messages.copy()
        function_messages.append(AIMessage(role="assistant", content=ai_response.content))
        
        for result in function_results:
            if result["success"]:
                function_messages.append(AIMessage(
                    role="function",
                    name=result["function"],
                    content=json.dumps(result["result"])
                ))
            else:
                function_messages.append(AIMessage(
                    role="function",
                    name=result["function"],
                    content=f"Error: {result.get('error', 'Unknown error')}"
                ))
        
        # Generate final response with function results
        final_response = await self.provider.chat_completion(
            messages=function_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return final_response.content
    
    async def generate_sales_insights(self) -> Dict[str, Any]:
        """Generate comprehensive sales insights"""
        user_context = self.data_access.get_user_context()
        org_context = self.data_access.get_organization_context()
        pipeline_summary = self.data_access.get_pipeline_summary()
        
        # Analyze performance
        performance = user_context.get("performance", {})
        win_rate = performance.get("win_rate", 0)
        total_value = performance.get("total_value", 0)
        
        # Generate insights using AI
        insights_prompt = f"""Analyze this sales data and provide actionable insights:

User Performance:
- Total Deals: {performance.get('total_deals', 0)}
- Total Value: ${performance.get('total_value', 0):,.0f}
- Win Rate: {win_rate:.1f}%

Organization Metrics:
- Total Pipeline Value: ${org_context.get('metrics', {}).get('pipeline_value', 0):,.0f}
- Total Contacts: {org_context.get('metrics', {}).get('total_contacts', 0)}
- Total Leads: {org_context.get('metrics', {}).get('total_leads', 0)}

Pipeline Summary:
{json.dumps(pipeline_summary, indent=2)}

Provide:
1. Key performance insights
2. Areas for improvement
3. Recommended actions
4. Pipeline optimization suggestions
5. Lead nurturing recommendations"""

        messages = [
            AIMessage(role="system", content="You are a sales analytics expert. Provide data-driven insights and actionable recommendations."),
            AIMessage(role="user", content=insights_prompt)
        ]
        
        response = await self.provider.chat_completion(messages=messages, temperature=0.3)
        
        return {
            "insights": response.content,
            "performance_metrics": performance,
            "pipeline_summary": pipeline_summary,
            "generated_at": datetime.now().isoformat()
        }
    
    async def suggest_next_actions(self, entity_type: str, entity_id: int) -> Dict[str, Any]:
        """Suggest next actions for a specific entity"""
        
        # Get entity context
        if entity_type == "lead":
            context = self.data_access.get_lead_context(entity_id)
        elif entity_type == "deal":
            context = self.data_access.get_deal_context(entity_id)
        elif entity_type == "contact":
            context = self.data_access.get_contact_context(entity_id)
        else:
            return {"error": "Invalid entity type"}
        
        # Generate suggestions using AI
        suggestions_prompt = f"""Based on this {entity_type} data, suggest the next best actions:

{json.dumps(context, indent=2)}

Provide:
1. Immediate next steps (next 1-2 days)
2. Medium-term actions (next week)
3. Long-term strategy (next month)
4. Email templates that would be appropriate
5. Follow-up timing recommendations
6. Risk factors to watch for

Be specific and actionable."""

        messages = [
            AIMessage(role="system", content="You are a sales strategy expert. Provide specific, actionable recommendations."),
            AIMessage(role="user", content=suggestions_prompt)
        ]
        
        response = await self.provider.chat_completion(messages=messages, temperature=0.5)
        
        return {
            "suggestions": response.content,
            "entity_context": context,
            "generated_at": datetime.now().isoformat()
        }
