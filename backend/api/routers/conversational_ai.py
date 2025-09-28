"""
Conversational AI API endpoints for Retell AI integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
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
    DemoScenario, DemoScenarioList, ConversationScenario, CallStatus
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
            raise HTTPException(status_code=500, detail="Failed to delete agent from Retell AI")
        
        # Remove from local storage
        del agents_storage[agent_id]
        
        logger.info(f"Deleted agent: {agent_id}")
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete agent")

@router.post("/calls", response_model=CallResponse)
async def create_call(
    call_data: CallCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new phone call"""
    try:
        # Validate agent exists
        if call_data.agent_id not in agents_storage:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = agents_storage[call_data.agent_id]
        
        # Create call in Retell AI
        call_id = await retell_ai_service.create_phone_call(
            agent_id=call_data.agent_id,
            to_number=call_data.to_number,
            from_number=call_data.from_number,
            metadata=call_data.call_metadata
        )
        
        if not call_id:
            raise HTTPException(status_code=500, detail="Failed to create call in Retell AI")
        
        # Store call locally
        call_response = CallResponse(
            call_id=call_id,
            agent_id=call_data.agent_id,
            to_number=call_data.to_number,
            from_number=call_data.from_number,
            status=CallStatus.PENDING,
            scenario=agent.scenario,
            created_at=datetime.utcnow()
        )
        
        calls_storage[call_id] = call_response
        
        # Store in database
        background_tasks.add_task(store_call_record, db, call_data, call_id)
        
        logger.info(f"Created call: {call_id}")
        return call_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating call: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create call")

@router.get("/calls", response_model=CallListResponse)
async def get_calls(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    scenario: Optional[ConversationScenario] = Query(None, description="Filter by scenario"),
    status: Optional[CallStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get call history"""
    try:
        calls = list(calls_storage.values())
        
        # Apply filters
        if scenario:
            calls = [call for call in calls if call.scenario == scenario]
        if status:
            calls = [call for call in calls if call.status == status]
        
        # Sort by creation date (newest first)
        calls.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(calls)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_calls = calls[start:end]
        
        return CallListResponse(
            calls=paginated_calls,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching calls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch calls")

@router.get("/calls/{call_id}", response_model=CallResponse)
async def get_call(call_id: str, db: Session = Depends(get_db)):
    """Get a specific call"""
    try:
        if call_id not in calls_storage:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Update call from Retell AI
        retell_call = await retell_ai_service.get_call(call_id)
        
        if retell_call:
            # Update local storage with latest data
            existing_call = calls_storage[call_id]
            existing_call.status = CallStatus(retell_call.status.lower())
            existing_call.start_time = retell_call.start_time
            existing_call.end_time = retell_call.end_time
            existing_call.duration = retell_call.duration
            existing_call.recording_url = retell_call.recording_url
            existing_call.transcript = retell_call.transcript
            existing_call.cost = retell_call.cost
        
        return calls_storage[call_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch call")

@router.get("/analytics", response_model=CallAnalytics)
async def get_call_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    scenario: Optional[ConversationScenario] = Query(None, description="Filter by scenario"),
    db: Session = Depends(get_db)
):
    """Get call analytics"""
    try:
        calls = list(calls_storage.values())
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        calls = [call for call in calls if call.created_at >= cutoff_date]
        
        # Filter by scenario if specified
        if scenario:
            calls = [call for call in calls if call.scenario == scenario]
        
        # Calculate analytics
        total_calls = len(calls)
        successful_calls = len([call for call in calls if call.status == CallStatus.COMPLETED])
        failed_calls = len([call for call in calls if call.status == CallStatus.FAILED])
        
        total_duration = sum(call.duration or 0 for call in calls)
        average_duration = total_duration / total_calls if total_calls > 0 else 0
        
        total_cost = sum(call.cost or 0 for call in calls)
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Scenario breakdown
        scenario_breakdown = {}
        for call in calls:
            scenario_breakdown[call.scenario.value] = scenario_breakdown.get(call.scenario.value, 0) + 1
        
        return CallAnalytics(
            total_calls=total_calls,
            successful_calls=successful_calls,
            failed_calls=failed_calls,
            total_duration=total_duration,
            average_duration=average_duration,
            total_cost=total_cost,
            success_rate=success_rate,
            scenario_breakdown=scenario_breakdown
        )
        
    except Exception as e:
        logger.error(f"Error calculating analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate analytics")

@router.post("/demo/create-agents")
async def create_demo_agents(db: Session = Depends(get_db)):
    """Create demo agents for all scenarios"""
    try:
        created_agents = await retell_ai_service.create_demo_agents()
        
        # Store demo agents locally
        scenarios = retell_ai_service.get_conversation_scenarios()
        
        for scenario_id, agent_id in created_agents.items():
            scenario_config = scenarios[scenario_id]
            
            agent_response = AgentResponse(
                agent_id=agent_id,
                name=scenario_config["name"],
                voice_id=scenario_config["voice_id"],
                language=scenario_config["language"],
                scenario=ConversationScenario(scenario_id),
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                config=scenario_config["llm_dynamic_config"]
            )
            
            agents_storage[agent_id] = agent_response
        
        logger.info(f"Created {len(created_agents)} demo agents")
        return {
            "message": f"Created {len(created_agents)} demo agents successfully",
            "agents": created_agents
        }
        
    except Exception as e:
        logger.error(f"Error creating demo agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create demo agents")

# Webhook endpoints for Retell AI callbacks
@router.post("/webhook/{scenario}")
async def handle_webhook(
    scenario: str,
    webhook_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle webhook events from Retell AI"""
    try:
        event_type = webhook_data.get("event_type")
        call_id = webhook_data.get("call_id")
        
        logger.info(f"Received webhook for scenario {scenario}: {event_type} - {call_id}")
        
        if call_id in calls_storage:
            call = calls_storage[call_id]
            
            # Update call status based on event type
            if event_type == "call_started":
                call.status = CallStatus.ANSWERED
                call.start_time = datetime.utcnow()
            elif event_type == "call_ended":
                call.status = CallStatus.COMPLETED
                call.end_time = datetime.utcnow()
                if call.start_time:
                    call.duration = int((call.end_time - call.start_time).total_seconds())
            elif event_type == "call_failed":
                call.status = CallStatus.FAILED
            elif event_type == "transcript":
                call.transcript = webhook_data.get("transcript", "")
            elif event_type == "recording":
                call.recording_url = webhook_data.get("recording_url", "")
            elif event_type == "cost":
                call.cost = webhook_data.get("cost", 0.0)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# Helper function to store call record in database
async def store_call_record(db: Session, call_data: CallCreate, call_id: str):
    """Store call record in database"""
    try:
        call_record = CallRecord(
            external_call_id=call_id,
            agent_id=call_data.agent_id,
            to_number=call_data.to_number,
            from_number=call_data.from_number,
            scenario=call_data.scenario.value,
            status="pending",
            call_metadata=call_data.call_metadata,
            lead_id=call_data.lead_id,
            contact_id=call_data.contact_id,
            user_id=call_data.user_id
        )
        
        db.add(call_record)
        db.commit()
        logger.info(f"Stored call record in database: {call_id}")
        
    except Exception as e:
        logger.error(f"Error storing call record: {str(e)}")
        db.rollback()
