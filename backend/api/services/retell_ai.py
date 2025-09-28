"""
Retell AI Integration for Conversational AI Voice Agents
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from pydantic import BaseModel
import os
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class RetellAIVoice(BaseModel):
    """Retell AI Voice Model"""
    voice_id: str
    name: str
    voice_type: str
    description: str
    language: str
    gender: str
    accent: str
    sample_url: Optional[str] = None

class RetellAIAgent(BaseModel):
    """Retell AI Agent Configuration"""
    agent_id: Optional[str] = None
    name: str
    voice_id: str
    language: str
    llm_dynamic_config: Dict[str, Any]
    real_time_transcription: bool = True
    real_time_ai_thoughts: bool = False
    end_call_message: str = "Thank you for calling. Have a great day!"
    end_call_phrases: List[str] = ["goodbye", "bye", "end call", "hang up"]
    interruptions_threshold: int = 2
    backchannel_frequency: float = 0.3
    backchannel_threshold: float = 0.7
    normalize_for_speech: bool = True
    webhook_url: Optional[str] = None
    webhook_url_auth_header: Optional[str] = None
    max_duration_seconds: int = 1800  # 30 minutes
    enable_transcription_formatting: bool = True

class RetellAICall(BaseModel):
    """Retell AI Call Model"""
    call_id: str
    agent_id: str
    from_number: str
    to_number: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ConversationContext(BaseModel):
    """Context for conversational AI"""
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []
    current_scenario: str = "general"
    caller_info: Optional[Dict[str, Any]] = None
    lead_data: Optional[Dict[str, Any]] = None
    crm_data: Optional[Dict[str, Any]] = None

class RetellAIService:
    """Retell AI Service for voice conversations and call management"""
    
    def __init__(self):
        self.api_key = os.getenv("RETELL_AI_API_KEY")
        self.base_url = "https://api.retellai.com"
        self.webhook_base_url = os.getenv("WEBHOOK_BASE_URL", "https://your-domain.com")
        
        if not self.api_key:
            logger.warning("RETELL_AI_API_KEY not found in environment variables")
    
    async def get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_voices(self) -> List[RetellAIVoice]:
        """Get available voices from Retell AI"""
        if not self.api_key:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/list-voices",
                    headers=await self.get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                voices_data = response.json()
                voices = []
                
                # Handle both list and dict response formats
                if isinstance(voices_data, list):
                    voice_list = voices_data
                else:
                    voice_list = voices_data.get("voices", [])
                
                for voice in voice_list:
                    voices.append(RetellAIVoice(
                        voice_id=voice["voice_id"],
                        name=voice.get("voice_name", voice.get("name", voice["voice_id"])),
                        voice_type=voice.get("voice_type", "unknown"),
                        description=voice.get("description", ""),
                        language=voice.get("language", "en"),
                        gender=voice.get("gender", "unknown"),
                        accent=voice.get("accent", "unknown"),
                        sample_url=voice.get("preview_audio_url")
                    ))
                
                return voices
                
        except Exception as e:
            logger.error(f"Error fetching voices from Retell AI: {str(e)}")
            return []
    
    async def create_retell_llm(self, llm_config: Dict[str, Any]) -> Optional[str]:
        """Create a Retell LLM first"""
        if not self.api_key:
            raise ValueError("Retell AI API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-retell-llm",
                    headers=await self.get_headers(),
                    json=llm_config,
                    timeout=60.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    llm_id = result.get("llm_id")
                    logger.info(f"Created Retell LLM with ID: {llm_id}")
                    return llm_id
                else:
                    error_detail = response.text
                    logger.error(f"Retell LLM creation error {response.status_code}: {error_detail}")
                    return None
                
        except Exception as e:
            logger.error(f"Error creating Retell LLM: {str(e)}")
            return None

    async def create_agent(self, agent_config: RetellAIAgent) -> Optional[str]:
        """Create a new Retell AI agent"""
        if not self.api_key:
            raise ValueError("Retell AI API key not configured")
        
        try:
            # First create a Retell LLM
            llm_config = {
                "model": agent_config.llm_dynamic_config.get("model", "gpt-4o"),
                "model_temperature": agent_config.llm_dynamic_config.get("temperature", 0.7),
                "general_prompt": agent_config.llm_dynamic_config.get("system_prompt", "You are a helpful AI assistant."),
                "general_tools": [
                    {
                        "type": "end_call",
                        "name": "end_call",
                        "description": "End the call with user."
                    }
                ],
                "states": [
                    {
                        "name": "main_conversation",
                        "state_prompt": agent_config.llm_dynamic_config.get("system_prompt", "You are a helpful AI assistant."),
                        "tools": []
                    }
                ],
                "starting_state": "main_conversation",
                "begin_message": agent_config.end_call_message or "Hello! How can I help you today?"
            }
            
            llm_id = await self.create_retell_llm(llm_config)
            if not llm_id:
                logger.error("Failed to create Retell LLM")
                return None
            
            # Now create the agent using the LLM
            payload = {
                "name": agent_config.name,
                "voice_id": agent_config.voice_id,
                "response_engine": {
                    "llm_id": llm_id,
                    "type": "retell-llm"
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-agent",
                    headers=await self.get_headers(),
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    agent_id = result.get("agent_id")
                    logger.info(f"Created Retell AI agent with ID: {agent_id}")
                    return agent_id
                else:
                    error_detail = response.text
                    logger.error(f"Retell AI agent creation error {response.status_code}: {error_detail}")
                    return None
                
        except Exception as e:
            logger.error(f"Error creating Retell AI agent: {str(e)}")
            return None
    
    async def get_agent(self, agent_id: str) -> Optional[RetellAIAgent]:
        """Get agent configuration"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-agent/{agent_id}",
                    headers=await self.get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                agent_data = response.json()
                return RetellAIAgent(
                    agent_id=agent_data.get("agent_id"),
                    name=agent_data.get("name"),
                    voice_id=agent_data.get("voice_id"),
                    language=agent_data.get("language"),
                    llm_dynamic_config=agent_data.get("llm_dynamic_config", {}),
                    real_time_transcription=agent_data.get("real_time_transcription", True),
                    real_time_ai_thoughts=agent_data.get("real_time_ai_thoughts", False),
                    end_call_message=agent_data.get("end_call_message", ""),
                    end_call_phrases=agent_data.get("end_call_phrases", []),
                    interruptions_threshold=agent_data.get("interruptions_threshold", 2),
                    backchannel_frequency=agent_data.get("backchannel_frequency", 0.3),
                    backchannel_threshold=agent_data.get("backchannel_threshold", 0.7),
                    normalize_for_speech=agent_data.get("normalize_for_speech", True),
                    webhook_url=agent_data.get("webhook_url"),
                    webhook_url_auth_header=agent_data.get("webhook_url_auth_header"),
                    max_duration_seconds=agent_data.get("max_duration_seconds", 1800),
                    enable_transcription_formatting=agent_data.get("enable_transcription_formatting", True)
                )
                
        except Exception as e:
            logger.error(f"Error fetching agent: {str(e)}")
            return None
    
    async def update_agent(self, agent_id: str, agent_config: RetellAIAgent) -> bool:
        """Update agent configuration"""
        if not self.api_key:
            return False
        
        try:
            payload = {
                "name": agent_config.name,
                "voice_id": agent_config.voice_id,
                "language": agent_config.language,
                "response_engine": {
                    "type": "custom_function"
                },  # Required field
                "llm_dynamic_config": agent_config.llm_dynamic_config,
                "real_time_transcription": agent_config.real_time_transcription,
                "real_time_ai_thoughts": agent_config.real_time_ai_thoughts,
                "end_call_message": agent_config.end_call_message,
                "end_call_phrases": agent_config.end_call_phrases,
                "interruptions_threshold": agent_config.interruptions_threshold,
                "backchannel_frequency": agent_config.backchannel_frequency,
                "backchannel_threshold": agent_config.backchannel_threshold,
                "normalize_for_speech": agent_config.normalize_for_speech,
                "webhook_url": agent_config.webhook_url,
                "webhook_url_auth_header": agent_config.webhook_url_auth_header,
                "max_duration_seconds": agent_config.max_duration_seconds,
                "enable_transcription_formatting": agent_config.enable_transcription_formatting
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/update-agent/{agent_id}",
                    headers=await self.get_headers(),
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Error updating agent: {str(e)}")
            return False
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/delete-agent/{agent_id}",
                    headers=await self.get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Error deleting agent: {str(e)}")
            return False
    
    async def create_phone_call(
        self,
        agent_id: str,
        to_number: str,
        from_number: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a phone call using Retell AI"""
        if not self.api_key:
            raise ValueError("Retell AI API key not configured")
        
        try:
            # For demo purposes, we'll simulate call creation since the actual endpoint
            # appears to be different or not publicly available
            # In a production environment, you would need to:
            # 1. Contact Retell AI support for the correct call creation endpoint
            # 2. Set up webhook endpoints for call status updates
            # 3. Use their SDK if available
            
            # Generate a simulated call ID for demo purposes
            import uuid
            call_id = f"call_{uuid.uuid4().hex[:16]}"
            
            logger.info(f"Simulated call creation - Agent: {agent_id}, To: {to_number}, Call ID: {call_id}")
            logger.info("Note: This is a demo simulation. For production, contact Retell AI for call creation endpoint.")
            
            # In a real implementation, you would:
            # 1. Make the actual API call to create the call
            # 2. Set up webhooks to receive call status updates
            # 3. Store the call record in the database
            
            return call_id
                
        except Exception as e:
            logger.error(f"Error creating phone call: {str(e)}")
            return None
    
    async def get_call(self, call_id: str) -> Optional[RetellAICall]:
        """Get call details"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-call/{call_id}",
                    headers=await self.get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                call_data = response.json()
                return RetellAICall(
                    call_id=call_data.get("call_id"),
                    agent_id=call_data.get("agent_id"),
                    from_number=call_data.get("from_number"),
                    to_number=call_data.get("to_number"),
                    status=call_data.get("status"),
                    start_time=call_data.get("start_time"),
                    end_time=call_data.get("end_time"),
                    duration=call_data.get("duration"),
                    recording_url=call_data.get("recording_url"),
                    transcript=call_data.get("transcript"),
                    cost=call_data.get("cost"),
                    metadata=call_data.get("metadata")
                )
                
        except Exception as e:
            logger.error(f"Error fetching call: {str(e)}")
            return None
    
    def get_conversation_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined conversation scenarios for different CRM use cases"""
        return {
            "sales_outbound": {
                "name": "Sales Outbound Call",
                "description": "Professional sales call to generate leads and qualify prospects",
                "voice_id": "sarah_chen",  # Professional female voice
                "language": "en-US",
                "llm_dynamic_config": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 150,
                    "system_prompt": """You are Sarah, a professional sales representative from NeuraCRM. 
                    You're calling to introduce our AI-powered CRM solution that helps businesses streamline operations.
                    Be friendly, professional, and focus on understanding their current business challenges.
                    Keep responses concise and natural for phone conversations.
                    If they're interested, ask qualifying questions about their team size, current CRM usage, and pain points."""
                },
                "end_call_message": "Thank you for your time today. I'll send you some information about NeuraCRM via email. Have a great day!",
                "end_call_phrases": ["not interested", "not now", "goodbye", "bye", "end call"],
                "webhook_url": f"{self.webhook_base_url}/api/conversational-ai/webhook/sales",
                "max_duration_seconds": 900  # 15 minutes
            },
            "customer_support": {
                "name": "Customer Support Call",
                "description": "Helpful customer support interaction to resolve issues",
                "voice_id": "alex_rodriguez",  # Friendly male voice
                "language": "en-US",
                "llm_dynamic_config": {
                    "model": "gpt-4o",
                    "temperature": 0.5,
                    "max_tokens": 200,
                    "system_prompt": """You are Alex, a customer support specialist from NeuraCRM.
                    You're here to help resolve customer issues and provide excellent support.
                    Be empathetic, patient, and solution-focused. Ask clarifying questions to understand the problem.
                    Provide step-by-step solutions and offer to follow up if needed.
                    Keep responses clear and actionable for phone conversations."""
                },
                "end_call_message": "I'm glad I could help resolve your issue today. Is there anything else I can assist you with?",
                "end_call_phrases": ["that's all", "goodbye", "bye", "thank you"],
                "webhook_url": f"{self.webhook_base_url}/api/conversational-ai/webhook/support",
                "max_duration_seconds": 1200  # 20 minutes
            },
            "lead_qualification": {
                "name": "Lead Qualification Call",
                "description": "Qualify leads and gather information for sales follow-up",
                "voice_id": "michael_johnson",  # Professional male voice
                "language": "en-US",
                "llm_dynamic_config": {
                    "model": "gpt-4o",
                    "temperature": 0.6,
                    "max_tokens": 180,
                    "system_prompt": """You are Michael, a lead qualification specialist from NeuraCRM.
                    You're calling to understand the prospect's needs and determine if NeuraCRM is a good fit.
                    Ask about their current business processes, team size, pain points, and budget considerations.
                    Be consultative and focus on understanding their challenges rather than pushing the product.
                    Keep responses conversational and natural for phone calls."""
                },
                "end_call_message": "Thank you for sharing that information. I'll have our sales team reach out with a personalized solution. Have a great day!",
                "end_call_phrases": ["not interested", "not now", "goodbye", "bye"],
                "webhook_url": f"{self.webhook_base_url}/api/conversational-ai/webhook/qualification",
                "max_duration_seconds": 600  # 10 minutes
            },
            "appointment_booking": {
                "name": "Appointment Booking Call",
                "description": "Schedule appointments and demos for qualified prospects",
                "voice_id": "jessica_williams",  # Professional female voice
                "language": "en-US",
                "llm_dynamic_config": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 120,
                    "system_prompt": """You are Jessica, an appointment coordinator from NeuraCRM.
                    You're calling to schedule a personalized demo for qualified prospects.
                    Be flexible with scheduling and offer multiple time options.
                    Confirm contact details and send calendar invites.
                    Keep the conversation brief and focused on scheduling.
                    Be enthusiastic about showing them how NeuraCRM can help their business."""
                },
                "end_call_message": "Perfect! I'll send you a calendar invite with all the details. Looking forward to showing you NeuraCRM in action!",
                "end_call_phrases": ["not interested", "not now", "goodbye", "bye"],
                "webhook_url": f"{self.webhook_base_url}/api/conversational-ai/webhook/booking",
                "max_duration_seconds": 300  # 5 minutes
            }
        }
    
    async def create_demo_agents(self) -> Dict[str, str]:
        """Create demo agents for all scenarios"""
        scenarios = self.get_conversation_scenarios()
        created_agents = {}
        
        # First, get available voices
        voices = await self.get_voices()
        if not voices:
            logger.error("No voices available from Retell AI")
            return {}
        
        # Use the first available voice for all demo agents
        voice_id = voices[0].voice_id
        logger.info(f"Using voice ID: {voice_id} for demo agents")
        
        for scenario_id, scenario_config in scenarios.items():
            agent_config = RetellAIAgent(
                name=scenario_config["name"],
                voice_id=voice_id,  # Use real voice ID from API
                language=scenario_config["language"],
                llm_dynamic_config=scenario_config["llm_dynamic_config"],
                end_call_message=scenario_config["end_call_message"],
                end_call_phrases=scenario_config["end_call_phrases"],
                webhook_url=scenario_config["webhook_url"],
                max_duration_seconds=scenario_config["max_duration_seconds"],
                real_time_transcription=True,
                real_time_ai_thoughts=False,
                interruptions_threshold=2,
                backchannel_frequency=0.3,
                backchannel_threshold=0.7,
                normalize_for_speech=True,
                enable_transcription_formatting=True
            )
            
            agent_id = await self.create_agent(agent_config)
            if agent_id:
                created_agents[scenario_id] = agent_id
                logger.info(f"Created agent for scenario {scenario_id}: {agent_id}")
            else:
                logger.error(f"Failed to create agent for scenario {scenario_id}")
        
        return created_agents

# Global instance
retell_ai_service = RetellAIService()
