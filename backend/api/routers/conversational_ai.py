
"""
Conversational AI API endpoints for Retell AI integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from api.db import get_db
from api.models import User, Lead, Contact, CallRecord
from api.schemas.conversational_ai import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse,
    CallCreate, CallResponse, CallUpdate, CallListResponse,
    VoiceListResponse, ConversationContext, CallAnalytics,
    DemoScenario, DemoScenarioList, ConversationScenario, CallStatus,
    TranscriptEntry, AIThoughtEntry
)
from api.services.retell_ai import retell_ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversational-ai", tags=["Conversational AI"])

# In-memory storage for demo purposes (replace with database in production)
agents_storage: Dict[str, AgentResponse] = {}
calls_storage: Dict[str, CallResponse] = {}

@router.get("/voices", response_model=VoiceListResponse)
async def get_voices():
    """Get available voices from Retell AI"""
    try:
        voices = await retell_ai_service.get_voices()
        
        voice_configs = []
        for voice in voices:
            voice_configs.append({
                "voice_id": voice.voice_id,
                "name": voice.name,
                "language": voice.language,
                "gender": voice.gender,
                "accent": voice.accent
            })
        
        return VoiceListResponse(
            voices=voice_configs,
            total=len(voice_configs)
        )
        
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch voices")

@router.get("/scenarios", response_model=DemoScenarioList)
async def get_demo_scenarios():
    """Get available demo scenarios"""
    try:
        scenarios_config = retell_ai_service.get_conversation_scenarios()

        scenarios = []
        for scenario_id, config in scenarios_config.items():
            scenarios.append(DemoScenario(
                scenario_id=scenario_id,
                name=config["name"],
                description=config["description"],
                voice_id=config["voice_id"],
                language=config["language"],
                system_prompt=config["llm_dynamic_config"]["system_prompt"],
                end_call_message=config["end_call_message"],
                max_duration=config["max_duration_seconds"],
                webhook_url=config["webhook_url"],
                sample_script=[
                    "Hello! This is {agent_name} from NeuraCRM.",
                    "I'm calling to introduce our AI-powered CRM solution.",
                    "How are you doing today?",
                    "What's your current business size?",
                    "What challenges are you facing with your current processes?",
                    "Would you be interested in a personalized demo?",
                    "Thank you for your time. Have a great day!"
                ]
            ))

        return DemoScenarioList(
            scenarios=scenarios,
            total=len(scenarios)
        )

    except Exception as e:
        logger.error(f"Error fetching scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch scenarios")

@router.post("/demo/create-agents")
async def create_demo_agents(db: Session = Depends(get_db)):
    """Create demo agents for testing purposes"""
    try:
        demo_agents = []
        scenarios_config = retell_ai_service.get_conversation_scenarios()

        for scenario_id, config in scenarios_config.items():
            # Create agent for each scenario
            from api.services.retell_ai import RetellAIAgent

            retell_agent = RetellAIAgent(
                name=f"Demo {config['name']} Agent",
                voice_id=config["voice_id"],
                language=config["language"],
                llm_dynamic_config=config["llm_dynamic_config"],
                end_call_message=config["end_call_message"],
                end_call_phrases=["Thank you for your time", "Goodbye", "Have a great day"],
                max_duration_seconds=config["max_duration_seconds"],
                real_time_transcription=True,
                real_time_ai_thoughts=True,
                webhook_url=f"{retell_ai_service.webhook_base_url}/api/conversational-ai/webhook/{scenario_id}"
            )

            agent_id = await retell_ai_service.create_agent(retell_agent)

            if agent_id:
                # Determine if this is a demo agent (when real API is unavailable)
                is_demo_agent = agent_id.startswith("demo_agent_")
                agent_status = "demo" if is_demo_agent else "active"

                # Store agent locally
                agent_response = AgentResponse(
                    agent_id=agent_id,
                    name=f"Demo {config['name']} Agent" + (" (Demo Mode)" if is_demo_agent else ""),
                    voice_id=config["voice_id"],
                    language=config["language"],
                    scenario=ConversationScenario(scenario_id),
                    status=agent_status,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    config={
                        "temperature": config["llm_dynamic_config"].get("temperature", 0.7),
                        "max_tokens": config["llm_dynamic_config"].get("max_tokens", 150),
                        "system_prompt": config["llm_dynamic_config"]["system_prompt"],
                        "end_call_message": config["end_call_message"],
                        "end_call_phrases": ["Thank you for your time", "Goodbye", "Have a great day"],
                        "max_duration_seconds": config["max_duration_seconds"],
                        "enable_transcription": True,
                        "enable_ai_thoughts": True,
                        "demo_mode": is_demo_agent
                    }
                )

                agents_storage[agent_id] = agent_response
                demo_agents.append(agent_response)

                logger.info(f"Created demo agent: {agent_id} for scenario {scenario_id}")

        # Check if any agents are in demo mode
        has_demo_agents = any(agent.status == "demo" for agent in demo_agents)
        has_real_agents = any(agent.status == "active" for agent in demo_agents)

        if has_demo_agents and not has_real_agents:
            message = f"Created {len(demo_agents)} demo agents (Retell AI API unavailable - using demo mode)"
        elif has_demo_agents and has_real_agents:
            real_count = sum(1 for agent in demo_agents if agent.status == "active")
            demo_count = sum(1 for agent in demo_agents if agent.status == "demo")
            message = f"Created {real_count} real agents and {demo_count} demo agents"
        else:
            message = f"Successfully created {len(demo_agents)} demo agents"

        return {
            "message": message,
            "agents": [{"agent_id": agent.agent_id, "name": agent.name, "scenario": agent.scenario.value, "status": agent.status} for agent in demo_agents]
        }

    except Exception as e:
        logger.error(f"Error creating demo agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create demo agents")

@router.post("/agents", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new conversational AI agent"""
    try:
        # Create agent in Retell AI
        from api.services.retell_ai import RetellAIAgent
        
        retell_agent = RetellAIAgent(
            name=agent_data.name,
            voice_id=agent_data.voice_id,
            language=agent_data.language,
            llm_dynamic_config={
                "model": "gpt-4o",
                "temperature": agent_data.temperature,
                "max_tokens": agent_data.max_tokens,
                "system_prompt": agent_data.system_prompt
            },
            end_call_message=agent_data.end_call_message,
            end_call_phrases=agent_data.end_call_phrases,
            max_duration_seconds=agent_data.max_duration_seconds,
            real_time_transcription=agent_data.enable_transcription,
            real_time_ai_thoughts=agent_data.enable_ai_thoughts,
            webhook_url=f"{retell_ai_service.webhook_base_url}/api/conversational-ai/webhook/{agent_data.scenario.value}"
        )
        
        agent_id = await retell_ai_service.create_agent(retell_agent)
        
        if not agent_id:
            raise HTTPException(status_code=500, detail="Failed to create agent in Retell AI")
        
        # Store agent locally
        agent_response = AgentResponse(
            agent_id=agent_id,
            name=agent_data.name,
            voice_id=agent_data.voice_id,
            language=agent_data.language,
            scenario=agent_data.scenario,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            config={
                "temperature": agent_data.temperature,
                "max_tokens": agent_data.max_tokens,
                "system_prompt": agent_data.system_prompt,
                "end_call_message": agent_data.end_call_message,
                "end_call_phrases": agent_data.end_call_phrases,
                "max_duration_seconds": agent_data.max_duration_seconds,
                "enable_transcription": agent_data.enable_transcription,
                "enable_ai_thoughts": agent_data.enable_ai_thoughts
            }
        )
        
        agents_storage[agent_id] = agent_response
        
        logger.info(f"Created agent: {agent_id}")
        return agent_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create agent")

@router.get("/agents", response_model=AgentListResponse)
async def get_agents(
    scenario: Optional[ConversationScenario] = Query(None, description="Filter by scenario"),
    db: Session = Depends(get_db)
):
    """Get all conversational AI agents"""
    try:
        agents = list(agents_storage.values())
        
        if scenario:
            agents = [agent for agent in agents if agent.scenario == scenario]
        
        return AgentListResponse(
            agents=agents,
            total=len(agents)
        )
        
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agents")

@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a specific agent"""
    try:
        if agent_id not in agents_storage:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agents_storage[agent_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent")

@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing agent"""
    try:
        if agent_id not in agents_storage:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        existing_agent = agents_storage[agent_id]
        
        # Update Retell AI agent
        from api.services.retell_ai import RetellAIAgent
        
        retell_agent = RetellAIAgent(
            name=agent_data.name or existing_agent.name,
            voice_id=agent_data.voice_id or existing_agent.voice_id,
            language=agent_data.language or existing_agent.language,
            llm_dynamic_config={
                "model": "gpt-4o",
                "temperature": agent_data.temperature or existing_agent.config.get("temperature", 0.7),
                "max_tokens": agent_data.max_tokens or existing_agent.config.get("max_tokens", 150),
                "system_prompt": agent_data.system_prompt or existing_agent.config.get("system_prompt", "")
            },
            end_call_message=agent_data.end_call_message or existing_agent.config.get("end_call_message", ""),
            end_call_phrases=agent_data.end_call_phrases or existing_agent.config.get("end_call_phrases", []),
            max_duration_seconds=agent_data.max_duration_seconds or existing_agent.config.get("max_duration_seconds", 900),
            real_time_transcription=agent_data.enable_transcription if agent_data.enable_transcription is not None else existing_agent.config.get("enable_transcription", True),
            real_time_ai_thoughts=agent_data.enable_ai_thoughts if agent_data.enable_ai_thoughts is not None else existing_agent.config.get("enable_ai_thoughts", False),
            webhook_url=f"{retell_ai_service.webhook_base_url}/api/conversational-ai/webhook/{existing_agent.scenario.value}"
        )
        
        success = await retell_ai_service.update_agent(agent_id, retell_agent)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update agent in Retell AI")
        
        # Update local storage
        updated_agent = AgentResponse(
            agent_id=agent_id,
            name=agent_data.name or existing_agent.name,
            voice_id=agent_data.voice_id or existing_agent.voice_id,
            language=agent_data.language or existing_agent.language,
            scenario=agent_data.scenario or existing_agent.scenario,
            status=existing_agent.status,
            created_at=existing_agent.created_at,
            updated_at=datetime.utcnow(),
            config={
                "temperature": agent_data.temperature or existing_agent.config.get("temperature", 0.7),
                "max_tokens": agent_data.max_tokens or existing_agent.config.get("max_tokens", 150),
                "system_prompt": agent_data.system_prompt or existing_agent.config.get("system_prompt", ""),
                "end_call_message": agent_data.end_call_message or existing_agent.config.get("end_call_message", ""),
                "end_call_phrases": agent_data.end_call_phrases or existing_agent.config.get("end_call_phrases", []),
                "max_duration_seconds": agent_data.max_duration_seconds or existing_agent.config.get("max_duration_seconds", 900),
                "enable_transcription": agent_data.enable_transcription if agent_data.enable_transcription is not None else existing_agent.config.get("enable_transcription", True),
                "enable_ai_thoughts": agent_data.enable_ai_thoughts if agent_data.enable_ai_thoughts is not None else existing_agent.config.get("enable_ai_thoughts", False)
            }
        )
        
        agents_storage[agent_id] = updated_agent
        
        logger.info(f"Updated agent: {agent_id}")
        return updated_agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update agent")

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent"""
    try:
        if agent_id not in agents_storage:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Delete from Retell AI
        success = await retell_ai_service.delete_agent(agent_id)
        
        if not success:
            # Log but don't fail, allow local deletion
            logger.warning(f"Failed to delete agent {agent_id} from Retell AI, deleting locally.")
        
        # Delete from local storage
        del agents_storage[agent_id]
        
        logger.info(f"Deleted agent: {agent_id}")
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete agent")

# --- Call Management Endpoints ---

@router.post("/calls", response_model=CallResponse)
async def create_call(call_data: CallCreate, db: Session = Depends(get_db)):
    """Create and start a new phone call with CRM validation and PBX integration"""
    logger.info(f"🚀 STARTING CALL CREATION - Agent: {call_data.agent_id}, To: {call_data.to_number}")

    try:
        # Step 1: Check if agent exists
        logger.info(f"Step 1: Checking agent existence - Agent ID: {call_data.agent_id}")
        if call_data.agent_id not in agents_storage:
            logger.error(f"Agent not found in storage: {call_data.agent_id}")
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = agents_storage[call_data.agent_id]
        logger.info(f"Agent found: {agent.name} (Status: {agent.status})")

        # Step 2: Enhanced call creation with CRM validation and PBX integration
        logger.info("Step 2: Starting phone call creation with Retell AI service")

        metadata = {
            "lead_id": call_data.lead_id,
            "contact_id": call_data.contact_id,
            "scenario": agent.scenario.value,
            "user_id": getattr(call_data, 'user_id', None)
        }
        logger.info(f"Call metadata: {metadata}")

        call_id = await retell_ai_service.create_phone_call(
            agent_id=call_data.agent_id,
            to_number=call_data.to_number,
            from_number=None,  # Will be set by PBX provider config
            metadata=metadata,
            db=db
        )

        logger.info(f"Retell AI service returned call_id: {call_id}")

        if not call_id:
            logger.error("Retell AI service returned None call_id")
            raise HTTPException(status_code=500, detail="Failed to create call with Retell AI")

        # Step 3: Create call record in database for tracking
        logger.info("Step 3: Creating call record in database")
        call_record = CallRecord(
            external_call_id=call_id,
            agent_id=call_data.agent_id,
            to_number=call_data.to_number,
            scenario=agent.scenario.value,
            lead_id=call_data.lead_id,
            contact_id=call_data.contact_id
        )
        db.add(call_record)
        db.commit()
        logger.info("Call record committed to database")

        # Step 4: Create response object
        logger.info("Step 4: Creating response object")
        call_response = CallResponse(
            call_id=call_id,
            agent_id=call_data.agent_id,
            to_number=call_data.to_number,
            from_number=None,  # Will be determined by PBX provider
            status=CallStatus.PENDING,
            scenario=agent.scenario,
            start_time=datetime.utcnow(),
            created_at=datetime.utcnow(),
            call_metadata={
                "lead_id": call_data.lead_id,
                "contact_id": call_data.contact_id,
                "user_id": getattr(call_data, 'user_id', None)
            }
        )

        calls_storage[call_id] = call_response
        logger.info(f"Call response stored in memory: {call_id}")

        logger.info(f"✅ CALL CREATION COMPLETED SUCCESSFULLY - Call ID: {call_id}")
        return call_response

    except ValueError as e:
        # Handle validation errors specifically
        logger.warning(f"❌ Call validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        logger.warning(f"❌ HTTP Exception during call creation: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error creating call: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create call: {str(e)}")

@router.get("/calls", response_model=CallListResponse)
async def get_calls(
    status: Optional[CallStatus] = Query(None, description="Filter by call status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get a list of all calls"""
    try:
        all_calls = sorted(calls_storage.values(), key=lambda c: c.start_time, reverse=True)

        if status:
            all_calls = [call for call in all_calls if call.status == status]

        paginated_calls = all_calls[offset : offset + limit]

        # Calculate page number from offset and limit
        page = (offset // limit) + 1 if limit > 0 else 1

        return CallListResponse(
            calls=paginated_calls,
            total=len(all_calls),
            page=page,
            per_page=limit
        )
    except Exception as e:
        logger.error(f"Error fetching calls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch calls")

@router.get("/calls/{call_id}", response_model=CallResponse)
async def get_call(call_id: str):
    """Get details for a specific call"""
    if call_id not in calls_storage:
        raise HTTPException(status_code=404, detail="Call not found")
    return calls_storage[call_id]

@router.get("/analytics")
async def get_call_analytics(db: Session = Depends(get_db)):
    """Get call analytics data"""
    try:
        # Calculate basic analytics from stored calls
        total_calls = len(calls_storage)
        successful_calls = len([c for c in calls_storage.values() if c.status in ["completed", "answered"]])
        failed_calls = len([c for c in calls_storage.values() if c.status in ["failed", "busy", "no-answer"]])

        # Calculate duration stats
        completed_calls = [c for c in calls_storage.values() if c.duration and c.duration > 0]
        total_duration = sum(c.duration for c in completed_calls) if completed_calls else 0
        average_duration = total_duration / len(completed_calls) if completed_calls else 0

        # Calculate cost stats
        total_cost = sum(c.cost for c in calls_storage.values() if c.cost) or 0

        # Calculate success rate
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

        # Scenario breakdown
        scenario_breakdown = {}
        for call in calls_storage.values():
            scenario = call.scenario.value if hasattr(call.scenario, 'value') else str(call.scenario)
            scenario_breakdown[scenario] = scenario_breakdown.get(scenario, 0) + 1

        analytics = {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "total_duration": total_duration,
            "average_duration": average_duration,
            "total_cost": total_cost,
            "success_rate": success_rate,
            "scenario_breakdown": scenario_breakdown
        }

        return analytics

    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

# --- Webhook Endpoint ---

@router.post("/webhook/{scenario}")
async def handle_webhook(scenario: ConversationScenario, request: Request):
    """Handle real-time call events from Retell AI"""
    try:
        event_data = await request.json()
        call_id = event_data.get("call_id")
        event_type = event_data.get("event")
        
        logger.info(f"Webhook received for call {call_id}, event: {event_type}, scenario: {scenario.value}")

        if not call_id or call_id not in calls_storage:
            logger.warning(f"Webhook for unknown or untracked call_id: {call_id}")
            # Return 200 OK to prevent Retell from retrying.
            return {"status": "ok", "message": "Call ID not tracked"}

        call = calls_storage[call_id]
        
        if event_type == "call_started":
            call.status = CallStatus.IN_PROGRESS
            call.start_time = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))
            logger.info(f"Call {call_id} started.")

        elif event_type == "call_ended":
            call.status = CallStatus.ENDED
            call.end_time = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))
            if call.start_time:
                call.duration = (call.end_time - call.start_time).total_seconds()

            analysis = event_data.get("analysis", {})
            summary = analysis.get("summary")

            # Store summary and recording in call metadata
            if not call.call_metadata:
                call.call_metadata = {}
            if summary:
                call.call_metadata["summary"] = summary
            if "recording_url" in event_data:
                call.call_metadata["recording_url"] = event_data["recording_url"]

            logger.info(f"Call {call_id} ended. Duration: {call.duration}s. Summary: {summary}")
            # Here you could trigger post-call CRM actions, like creating a task or note.

        elif event_type == "transcript_updated":
            # Store transcript in call metadata since schema doesn't have transcript field
            transcript_data = event_data.get("transcript", [])
            if transcript_data:
                if not call.call_metadata:
                    call.call_metadata = {}
                call.call_metadata["transcript"] = transcript_data
            logger.debug(f"Transcript updated for call {call_id}")

        elif event_type == "ai_thought_updated":
            # Store AI thoughts in call metadata since schema doesn't have ai_thoughts field
            thoughts_data = event_data.get("thoughts", [])
            if thoughts_data:
                if not call.call_metadata:
                    call.call_metadata = {}
                call.call_metadata["ai_thoughts"] = thoughts_data
            logger.debug(f"AI thoughts updated for call {call_id}")

        else:
            logger.info(f"Received unhandled event type: {event_type} for call {call_id}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        # Return a 500 error to indicate a problem on our end.
        raise HTTPException(status_code=500, detail="Error processing webhook")
