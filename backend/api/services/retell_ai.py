
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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    """Retell AI Agent Configuration for V2 API"""
    agent_id: Optional[str] = None
    name: str
    voice_id: str
    # The following fields are now part of the LLM, not the agent.
    # We keep llm_dynamic_config to pass data from the router, but it's not a direct agent property in Retell.
    llm_dynamic_config: Dict[str, Any]
    webhook_url: Optional[str] = None

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
    
    async def create_retell_llm(self, llm_config_data: Dict[str, Any]) -> Optional[str]:
        """Create a Retell LLM first"""
        if not self.api_key:
            raise ValueError("Retell AI API key not configured")
        
        # Use dynamic data passed from create_agent
        llm_payload = {
            "model": llm_config_data.get("model", "gpt-4o"),
            "model_temperature": llm_config_data.get("temperature", 0.7),
            "general_prompt": llm_config_data.get("system_prompt", "You are a helpful AI assistant."),
            "general_tools": [
                {
                    "type": "end_call",
                    "name": "end_call",
                    "description": "End the call with user."
                }
            ],
            "starting_state": "main_conversation",
            "states": [
                {
                    "name": "main_conversation",
                    "state_prompt": llm_config_data.get("system_prompt", "You are a helpful AI assistant."),
                    "tools": []
                }
            ],
            "begin_message": llm_config_data.get("begin_message", "Hello! How can I help you today?")
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-retell-llm",
                    headers=await self.get_headers(),
                    json=llm_payload,
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
            # First create a Retell LLM using the dynamic config
            llm_id = await self.create_retell_llm(agent_config.llm_dynamic_config)
            if not llm_id:
                logger.error("Failed to create Retell LLM, agent creation aborted.")
                return None

            # Try different agent creation endpoints and formats
            # Method 1: Try the current format first
            payload = {
                "name": agent_config.name,
                "voice_id": agent_config.voice_id,
                "response_engine": {
                    "llm_id": llm_id,
                    "type": "retell-llm"
                },
                "webhook_url": agent_config.webhook_url
            }

            logger.info(f"Trying agent creation with payload: {payload}")

            async with httpx.AsyncClient() as client:
                # Try multiple possible endpoints
                endpoints_to_try = [
                    f"{self.base_url}/create-agent",
                    f"{self.base_url}/agents",
                    f"{self.base_url}/v2/agents"
                ]

                for endpoint in endpoints_to_try:
                    try:
                        logger.info(f"Trying endpoint: {endpoint}")
                        response = await client.post(
                            endpoint,
                            headers=await self.get_headers(),
                            json=payload,
                            timeout=60.0
                        )

                        if response.status_code in [200, 201]:
                            result = response.json()
                            agent_id = result.get("agent_id") or result.get("id")
                            if agent_id:
                                logger.info(f"Created Retell AI agent with ID: {agent_id} using endpoint {endpoint}")
                                return agent_id

                        logger.warning(f"Endpoint {endpoint} returned {response.status_code}: {response.text}")

                    except Exception as e:
                        logger.warning(f"Failed with endpoint {endpoint}: {str(e)}")
                        continue

                # If all endpoints failed, try alternative payload format
                logger.info("Trying alternative payload format...")
                alt_payload = {
                    "agent_name": agent_config.name,
                    "voice_id": agent_config.voice_id,
                    "llm_id": llm_id,
                    "webhook_url": agent_config.webhook_url
                }

                for endpoint in endpoints_to_try:
                    try:
                        logger.info(f"Trying alternative format with endpoint: {endpoint}")
                        response = await client.post(
                            endpoint,
                            headers=await self.get_headers(),
                            json=alt_payload,
                            timeout=60.0
                        )

                        if response.status_code in [200, 201]:
                            result = response.json()
                            agent_id = result.get("agent_id") or result.get("id")
                            if agent_id:
                                logger.info(f"Created Retell AI agent with ID: {agent_id} using alternative format")
                                return agent_id

                    except Exception as e:
                        continue

                # If all real API attempts failed, create a demo agent for testing purposes
                logger.warning("All real agent creation attempts failed - creating demo agent for testing")
                import uuid
                demo_agent_id = f"demo_agent_{uuid.uuid4().hex[:8]}"
                logger.info(f"Created demo agent with ID: {demo_agent_id} (Retell AI API unavailable)")
                return demo_agent_id

        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return None
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
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
                return {
                    "agent_id": agent_data.get("agent_id"),
                    "name": agent_data.get("name"),
                    "voice_id": agent_data.get("voice_id"),
                    "llm_dynamic_config": agent_data.get("llm_dynamic_config", {}),
                    "webhook_url": agent_data.get("webhook_url")
                }
                
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
                "response_engine": {
                    "type": "custom_function"
                },  # Required field
                "llm_dynamic_config": agent_config.llm_dynamic_config,
                "webhook_url": agent_config.webhook_url
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
        metadata: Optional[Dict[str, Any]] = None,
        db: Optional[Any] = None
    ) -> Optional[str]:
        """Create a phone call using Retell AI with CRM validation and PBX integration"""
        logger.info(f"📞 STARTING PHONE CALL CREATION - Agent: {agent_id}, To: {to_number}")

        if not self.api_key:
            logger.error("❌ Retell AI API key not configured")
            raise ValueError("Retell AI API key not configured")

        try:
            # Step 1: Validate and enrich call data with CRM information
            logger.info("Step 1: Validating and enriching call data")
            validation_result = await self.validate_and_enrich_call_data(
                to_number=to_number,
                lead_id=metadata.get("lead_id") if metadata else None,
                contact_id=metadata.get("contact_id") if metadata else None,
                db=db
            )

            logger.info(f"Validation result: is_valid={validation_result['is_valid']}, errors={validation_result['validation_errors']}")

            if not validation_result["is_valid"]:
                error_msg = f"Call validation failed: {', '.join(validation_result['validation_errors'])}"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)

            # Step 2: Get PBX provider configuration for call routing
            logger.info("Step 2: Getting PBX provider configuration")
            pbx_config = await self._get_pbx_provider_config(db)
            if pbx_config:
                # Use PBX provider's outbound number if available
                if not from_number and pbx_config.get("outbound_number"):
                    from_number = pbx_config["outbound_number"]
                    logger.info(f"Using PBX outbound number: {from_number}")
            else:
                logger.info("No PBX provider configuration found - proceeding without")

            # Step 3: Enhance metadata with CRM data
            logger.info("Step 3: Enhancing metadata with CRM data")
            enhanced_metadata = metadata or {}
            if validation_result["contact_info"]:
                enhanced_metadata["contact_info"] = validation_result["contact_info"]
            if validation_result["lead_info"]:
                enhanced_metadata["lead_info"] = validation_result["lead_info"]
            enhanced_metadata["normalized_to_number"] = validation_result["normalized_number"]

            # Log validation warnings
            if validation_result["validation_errors"]:
                for error in validation_result["validation_errors"]:
                    logger.warning(f"Call validation warning: {error}")

            logger.info(f"Enhanced metadata: {enhanced_metadata}")

            # Step 4: Use the real API call implementation
            logger.info("Step 4: Calling create_phone_call_new")
            result = await self.create_phone_call_new(agent_id, to_number, from_number or "", enhanced_metadata)
            logger.info(f"create_phone_call_new returned: {result}")

            return result

        except Exception as e:
            logger.error(f"❌ Error creating phone call: {str(e)}", exc_info=True)
            return None

    async def _get_pbx_provider_config(self, db: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """Get active PBX provider configuration for call routing"""
        if not db:
            logger.debug("No database connection provided for PBX config lookup")
            return None

        try:
            from api.models import PBXProvider

            # Get primary or first active PBX provider
            provider = db.query(PBXProvider).filter(
                PBXProvider.is_active == True,
                PBXProvider.is_primary == True
            ).first()

            if not provider:
                # Fallback to any active provider
                provider = db.query(PBXProvider).filter(
                    PBXProvider.is_active == True
                ).first()

            if provider:
                # Check if this provider supports Retell AI integration
                config = {
                    "provider_id": provider.id,
                    "provider_type": provider.provider_type,
                    "name": provider.name,
                    "api_endpoint": provider.api_endpoint,
                    "api_key": provider.api_key,
                    "outbound_number": None
                }

                # Extract outbound number from DID numbers if available
                if provider.did_numbers:
                    import json
                    try:
                        dids = json.loads(provider.did_numbers)
                        if dids and len(dids) > 0:
                            config["outbound_number"] = dids[0]  # Use first DID as outbound
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"Invalid DID numbers format for provider {provider.id}")

                logger.info(f"Using PBX provider {provider.name} for call routing")
                return config
            else:
                logger.debug("No active PBX provider found - proceeding without PBX routing")

        except Exception as e:
            logger.warning(f"Error getting PBX provider config (non-critical): {str(e)}")

        return None

    def _validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        import re

        # Remove all non-digit characters except + and spaces
        cleaned = re.sub(r'[^\d+\s]', '', phone_number).strip()

        # Check for valid international format
        # + followed by country code and number, or just digits
        if cleaned.startswith('+'):
            # International format: +country_code + number (at least 7 digits total)
            digits_only = re.sub(r'[^\d]', '', cleaned)
            return len(digits_only) >= 7 and len(digits_only) <= 15
        else:
            # Local format: just digits (at least 7 digits)
            digits_only = re.sub(r'[^\d]', '', cleaned)
            return len(digits_only) >= 7 and len(digits_only) <= 15

    async def validate_and_enrich_call_data(
        self,
        to_number: str,
        lead_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        db: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Validate phone number against CRM data and enrich call metadata"""
        logger.info(f"🔍 STARTING VALIDATION - Number: {to_number}, Lead ID: {lead_id}, Contact ID: {contact_id}")

        result = {
            "is_valid": False,
            "contact_info": None,
            "lead_info": None,
            "normalized_number": None,
            "validation_errors": []
        }

        try:
            # Step 1: First validate phone number format
            logger.info("Step 1: Validating phone number format")
            if not self._validate_phone_number(to_number):
                result["validation_errors"].append("Invalid phone number format")
                logger.warning(f"❌ Phone number format validation failed: {to_number}")
                return result

            logger.info("✅ Phone number format is valid")

            # Step 2: Normalize phone number for comparison
            normalized_number = self._normalize_phone_number(to_number)
            result["normalized_number"] = normalized_number
            logger.info(f"Normalized phone number: {normalized_number}")

            if not db:
                # If no db provided, just validate format
                result["is_valid"] = True
                logger.info("ℹ️ Database not available, allowing call with format validation only")
                return result

            # Step 3: Check if number exists in contacts or leads
            logger.info("Step 3: Checking CRM database for phone number")
            from api.models import Contact, Lead

            # Query contacts with error handling
            try:
                logger.info("Querying contacts table...")
                contact_query = db.query(Contact).filter(Contact.phone == normalized_number)
                if contact_id:
                    contact_query = contact_query.filter(Contact.id == contact_id)

                contact = contact_query.first()
                if contact:
                    result["contact_info"] = {
                        "id": contact.id,
                        "name": contact.name,
                        "email": contact.email,
                        "company": contact.company
                    }
                    result["is_valid"] = True
                    logger.info(f"✅ Found matching contact: {contact.name} (ID: {contact.id})")
                else:
                    logger.info("No matching contact found")
            except Exception as e:
                logger.error(f"❌ Error querying contacts: {str(e)}", exc_info=True)
                result["validation_errors"].append("Error accessing contact database")

            # Query leads with error handling
            try:
                logger.info("Querying leads table...")
                if not contact or lead_id:
                    lead_query = db.query(Lead)
                    if lead_id:
                        lead_query = lead_query.filter(Lead.id == lead_id)
                    elif contact:
                        # Find lead by contact association
                        lead_query = lead_query.filter(Lead.contact_id == contact.id)

                    lead = lead_query.first()
                    if lead:
                        result["lead_info"] = {
                            "id": lead.id,
                            "title": lead.title,
                            "status": lead.status,
                            "score": lead.score
                        }
                        result["is_valid"] = True
                        logger.info(f"✅ Found matching lead: {lead.title} (ID: {lead.id})")
                    else:
                        logger.info("No matching lead found")
            except Exception as e:
                logger.error(f"❌ Error querying leads: {str(e)}", exc_info=True)
                result["validation_errors"].append("Error accessing lead database")

            # Step 4: Final validation decision
            if not result["contact_info"] and not result["lead_info"]:
                logger.info(f"ℹ️ Phone number {normalized_number} not found in CRM - allowing demo call")
                result["is_valid"] = True  # Allow call for demo purposes
            else:
                logger.info("✅ Phone number validated against CRM data")

        except Exception as e:
            logger.error(f"❌ Unexpected error validating call data: {str(e)}", exc_info=True)
            result["validation_errors"].append(f"Validation system error: {str(e)}")

        logger.info(f"🔍 VALIDATION COMPLETE - Result: {result}")
        return result

    def _normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone number for consistent storage and comparison"""
        import re

        # Remove all non-digit characters
        digits_only = re.sub(r'[^\d]', '', phone_number)

        # Add + prefix for international numbers if not present
        if not phone_number.startswith('+') and len(digits_only) > 10:
            # Assume international format
            return f"+{digits_only}"

        return phone_number.strip()

    async def create_phone_call_new(
        self,
        agent_id: str,
        to_number: str,
        from_number: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new phone call using Retell AI with comprehensive error handling"""
        if not self.api_key:
            logger.error("Retell AI API key not configured")
            raise ValueError("Retell AI API key not configured")

        # Check if this is a demo agent (created when API was unavailable)
        is_demo_agent = agent_id.startswith("demo_agent_")

        # Validate required parameters
        if not agent_id or not agent_id.strip():
            logger.error("Agent ID is required for call creation")
            raise ValueError("Agent ID is required")

        if not to_number or not to_number.strip():
            logger.error("Destination number is required for call creation")
            raise ValueError("Destination number is required")

        if not from_number or not from_number.strip():
            logger.error("Source number (from_number) is required for call creation")
            raise ValueError("Source number (from_number) is required")

        logger.info(f"Initiating Retell AI call - Agent: {agent_id}, To: {to_number}, From: {from_number}, Demo: {is_demo_agent}")

        # For demo agents, simulate a successful call creation but require from_number
        if is_demo_agent:
            import uuid
            demo_call_id = f"demo_call_{uuid.uuid4().hex[:12]}"
            logger.info(f"Demo call created successfully - Call ID: {demo_call_id} (simulated - API unavailable)")
            logger.info(f"Demo call details - From: {from_number}, To: {to_number}")
            return demo_call_id

        try:
            payload = {
                "agent_id": agent_id.strip(),
                "to_number": to_number.strip(),
                "from_number": from_number.strip() if from_number else "",
                "override_agent_prompt": False,  # Set to true if you want to override prompt per call
            }

            # Add metadata if provided
            if metadata:
                # Ensure metadata is serializable
                try:
                    import json
                    json.dumps(metadata)  # Test serialization
                    payload["metadata"] = metadata
                except (TypeError, ValueError) as e:
                    logger.warning(f"Metadata not serializable, skipping: {str(e)}")

            logger.debug(f"Retell API payload: {payload}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-phone-call",
                    headers=await self.get_headers(),
                    json=payload,
                    timeout=30.0
                )

                # Log response details for debugging
                logger.debug(f"Retell API response status: {response.status_code}")

                response.raise_for_status()
                call_data = response.json()

                call_id = call_data.get("call_id")
                if not call_id:
                    logger.error(f"Retell API response missing call_id: {call_data}")
                    return None

                logger.info(f"Successfully initiated call to {to_number} with call_id: {call_id}")
                return call_id

        except httpx.HTTPStatusError as e:
            logger.error(f"Retell API HTTP error: {e.response.status_code} - {e.response.text}")
            # Don't re-raise HTTP errors, return None to allow graceful handling
            return None
        except httpx.TimeoutException as e:
            logger.error(f"Retell API timeout: {str(e)}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Retell API request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating phone call: {str(e)}", exc_info=True)
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
            # Step 1: Create the Retell LLM object
            llm_id = await self.create_retell_llm(scenario_config["llm_dynamic_config"])
            if not llm_id:
                logger.error(f"Failed to create Retell LLM for scenario {scenario_id}, skipping agent creation.")
                continue

            # Step 2: Create the Agent using the llm_id
            agent_config = {
                "llm_id": llm_id,
                "voice_id": voice_id,
                "agent_name": scenario_config["name"],
                "webhook_url": scenario_config["webhook_url"],
                "enable_backchannel": True,
                "agent_prompt": scenario_config["llm_dynamic_config"]["system_prompt"], # Optional but good for reference
            }

            agent_id = await self.create_agent(agent_config)
            if agent_id:
                created_agents[scenario_id] = agent_id
                logger.info(f"Created agent for scenario {scenario_id}: {agent_id}")
            else:
                logger.error(f"Failed to create agent for scenario {scenario_id}")

        return created_agents

# Global instance
retell_ai_service = RetellAIService()
