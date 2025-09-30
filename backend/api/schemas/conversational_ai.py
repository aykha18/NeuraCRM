
"""
Pydantic schemas for Conversational AI API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ConversationScenario(str, Enum):
    """Available conversation scenarios"""
    SALES_OUTBOUND = "sales_outbound"
    CUSTOMER_SUPPORT = "customer_support"
    LEAD_QUALIFICATION = "lead_qualification"
    APPOINTMENT_BOOKING = "appointment_booking"

class CallStatus(str, Enum):
    """Call status options"""
    PENDING = "pending"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    CANCELLED = "cancelled"

class VoiceConfig(BaseModel):
    """Voice configuration for Retell AI"""
    voice_id: str = Field(..., description="Retell AI voice ID")
    name: str = Field(..., description="Voice name")
    language: str = Field(default="en-US", description="Voice language")
    gender: Optional[str] = Field(None, description="Voice gender")
    accent: Optional[str] = Field(None, description="Voice accent")

class AgentConfig(BaseModel):
    """Agent configuration for conversational AI"""
    name: str = Field(..., description="Agent name")
    voice_id: str = Field(..., description="Retell AI voice ID")
    language: str = Field(default="en-US", description="Agent language")
    scenario: ConversationScenario = Field(..., description="Conversation scenario")
    system_prompt: str = Field(..., description="System prompt for the AI")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="AI temperature")
    max_tokens: int = Field(default=150, ge=50, le=500, description="Maximum tokens per response")
    end_call_message: str = Field(default="Thank you for calling. Have a great day!", description="End call message")
    end_call_phrases: List[str] = Field(default=["goodbye", "bye", "end call"], description="Phrases to end call")
    max_duration_seconds: int = Field(default=900, ge=60, le=3600, description="Maximum call duration")
    enable_transcription: bool = Field(default=True, description="Enable real-time transcription")
    enable_ai_thoughts: bool = Field(default=False, description="Enable AI thoughts logging")

class AgentCreate(BaseModel):
    """Schema for creating a new agent"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    voice_id: str = Field(..., description="Retell AI voice ID")
    language: str = Field(default="en-US", description="Agent language")
    scenario: ConversationScenario = Field(..., description="Conversation scenario")
    system_prompt: str = Field(..., min_length=10, max_length=2000, description="System prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="AI temperature")
    max_tokens: int = Field(default=150, ge=50, le=500, description="Maximum tokens")
    end_call_message: str = Field(default="Thank you for calling. Have a great day!", max_length=500)
    end_call_phrases: List[str] = Field(default=["goodbye", "bye", "end call"], max_items=10)
    max_duration_seconds: int = Field(default=900, ge=60, le=3600)
    enable_transcription: bool = Field(default=True)
    enable_ai_thoughts: bool = Field(default=False)

class AgentUpdate(BaseModel):
    """Schema for updating an existing agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    voice_id: Optional[str] = None
    language: Optional[str] = None
    scenario: Optional[ConversationScenario] = None
    system_prompt: Optional[str] = Field(None, min_length=10, max_length=2000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=50, le=500)
    end_call_message: Optional[str] = Field(None, max_length=500)
    end_call_phrases: Optional[List[str]] = Field(None, max_items=10)
    max_duration_seconds: Optional[int] = Field(None, ge=60, le=3600)
    enable_transcription: Optional[bool] = None
    enable_ai_thoughts: Optional[bool] = None

class AgentResponse(BaseModel):
    """Schema for agent response"""
    agent_id: str = Field(..., description="Retell AI agent ID")
    name: str = Field(..., description="Agent name")
    voice_id: str = Field(..., description="Voice ID")
    language: str = Field(..., description="Agent language")
    scenario: ConversationScenario = Field(..., description="Conversation scenario")
    status: str = Field(..., description="Agent status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    config: Dict[str, Any] = Field(..., description="Agent configuration")

class CallCreate(BaseModel):
    """Schema for creating a new call"""
    agent_id: str = Field(..., description="Retell AI agent ID")
    to_number: str = Field(..., description="Destination phone number")
    from_number: Optional[str] = Field(None, description="Source phone number")
    scenario: ConversationScenario = Field(..., description="Conversation scenario")
    call_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Call metadata")
    lead_id: Optional[int] = Field(None, description="Associated lead ID")
    contact_id: Optional[int] = Field(None, description="Associated contact ID")
    user_id: Optional[int] = Field(None, description="User who initiated the call")

    @validator('to_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        if not v or len(v) < 10:
            raise ValueError("Invalid phone number format")
        return v

class CallResponse(BaseModel):
    """Schema for call response"""
    call_id: str = Field(..., description="Retell AI call ID")
    agent_id: str = Field(..., description="Agent ID")
    to_number: str = Field(..., description="Destination number")
    from_number: Optional[str] = Field(None, description="Source number")
    status: CallStatus = Field(..., description="Call status")
    scenario: ConversationScenario = Field(..., description="Conversation scenario")
    start_time: Optional[datetime] = Field(None, description="Call start time")
    end_time: Optional[datetime] = Field(None, description="Call end time")
    duration: Optional[int] = Field(None, description="Call duration in seconds")
    recording_url: Optional[str] = Field(None, description="Call recording URL")
    transcript: Optional[str] = Field(None, description="Call transcript")
    cost: Optional[float] = Field(None, description="Call cost")
    call_metadata: Optional[Dict[str, Any]] = Field(None, description="Call metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

class CallUpdate(BaseModel):
    """Schema for updating call information"""
    status: Optional[CallStatus] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    cost: Optional[float] = None
    call_metadata: Optional[Dict[str, Any]] = None

class VoiceListResponse(BaseModel):
    """Schema for voice list response"""
    voices: List[VoiceConfig] = Field(..., description="Available voices")
    total: int = Field(..., description="Total number of voices")

class AgentListResponse(BaseModel):
    """Schema for agent list response"""
    agents: List[AgentResponse] = Field(..., description="Available agents")
    total: int = Field(..., description="Total number of agents")

class CallListResponse(BaseModel):
    """Schema for call list response"""
    calls: List[CallResponse] = Field(..., description="Call history")
    total: int = Field(..., description="Total number of calls")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")

class ConversationContext(BaseModel):
    """Schema for conversation context"""
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[int] = Field(None, description="User ID")
    lead_id: Optional[int] = Field(None, description="Lead ID")
    contact_id: Optional[int] = Field(None, description="Contact ID")
    scenario: ConversationScenario = Field(..., description="Conversation scenario")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    caller_info: Optional[Dict[str, Any]] = Field(None, description="Caller information")
    crm_data: Optional[Dict[str, Any]] = Field(None, description="CRM data")

class WebhookEvent(BaseModel):
    """Schema for webhook events"""
    event_type: str = Field(..., description="Event type")
    call_id: str = Field(..., description="Call ID")
    agent_id: str = Field(..., description="Agent ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")

class CallAnalytics(BaseModel):
    """Schema for call analytics"""
    total_calls: int = Field(..., description="Total number of calls")
    successful_calls: int = Field(..., description="Successful calls")
    failed_calls: int = Field(..., description="Failed calls")
    total_duration: int = Field(..., description="Total duration in seconds")
    average_duration: float = Field(..., description="Average call duration")
    total_cost: float = Field(..., description="Total cost")
    success_rate: float = Field(..., description="Success rate percentage")
    scenario_breakdown: Dict[str, int] = Field(..., description="Calls by scenario")

class DemoScenario(BaseModel):
    """Schema for demo scenarios"""
    scenario_id: str = Field(..., description="Scenario identifier")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    voice_id: str = Field(..., description="Recommended voice ID")
    language: str = Field(..., description="Language")
    system_prompt: str = Field(..., description="System prompt")
    end_call_message: str = Field(..., description="End call message")
    max_duration: int = Field(..., description="Maximum duration in seconds")
    webhook_url: str = Field(..., description="Webhook URL")
    sample_script: List[str] = Field(..., description="Sample conversation script")

class DemoScenarioList(BaseModel):
    """Schema for demo scenario list"""
    scenarios: List[DemoScenario] = Field(..., description="Available demo scenarios")
    total: int = Field(..., description="Total number of scenarios")

class TranscriptEntry(BaseModel):
    speaker: str
    text: str
    timestamp: datetime

class AIThoughtEntry(BaseModel):
    thought: str
    timestamp: datetime
