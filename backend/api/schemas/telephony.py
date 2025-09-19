from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for better type safety
class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"

class CallStatus(str, Enum):
    RINGING = "ringing"
    ANSWERED = "answered"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    FAILED = "failed"
    COMPLETED = "completed"

class CallDisposition(str, Enum):
    ANSWERED = "answered"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    FAILED = "failed"
    ABANDONED = "abandoned"

class ExtensionType(str, Enum):
    USER = "user"
    QUEUE = "queue"
    IVR = "ivr"
    CONFERENCE = "conference"
    VOICEMAIL = "voicemail"

class PresenceStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    AWAY = "away"
    OFFLINE = "offline"

class QueueStrategy(str, Enum):
    RINGALL = "ringall"
    LEASTRECENT = "leastrecent"
    FEWESTCALLS = "fewestcalls"
    RANDOM = "random"
    RRORDERED = "rrmemory"
    RRMEMORY = "rrmemory"
    LINEAR = "linear"
    WRANDOM = "wrandom"
    RRORDEREDHOLDLESS = "rrmemory"

class AgentStatus(str, Enum):
    LOGGED_IN = "logged_in"
    LOGGED_OUT = "logged_out"
    ON_BREAK = "on_break"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    OUTBOUND = "outbound"
    SURVEY = "survey"
    FOLLOW_UP = "follow_up"

# PBX Provider Schemas
class PBXProviderCreate(BaseModel):
    """Schema for creating a PBX provider"""
    name: str = Field(..., description="Provider name (e.g., 'Asterisk', 'FreePBX', '3CX')")
    provider_type: str = Field(..., description="Provider type: asterisk, freepbx, 3cx, twilio, custom")
    display_name: str = Field(..., description="Display name for the provider")
    description: Optional[str] = Field(None, description="Provider description")
    
    # Connection Settings
    host: str = Field(..., description="PBX host IP or domain")
    port: int = Field(8088, description="PBX port (AMI port for Asterisk)")
    username: str = Field(..., description="PBX username")
    password: str = Field(..., description="PBX password")
    api_key: Optional[str] = Field(None, description="API key for cloud providers")
    
    # PBX Configuration
    context: str = Field("default", description="Asterisk context")
    caller_id_field: str = Field("CallerIDNum", description="Field to extract caller ID")
    dialplan_context: str = Field("from-internal", description="Context for outbound calls")
    
    # Advanced Settings
    recording_enabled: bool = Field(True, description="Enable call recording")
    recording_path: str = Field("/var/spool/asterisk/monitor", description="Recording path")
    transcription_enabled: bool = Field(False, description="Enable call transcription")
    cdr_enabled: bool = Field(True, description="Enable CDR collection")
    cdr_path: str = Field("/var/log/asterisk/cdr-csv", description="CDR path")
    
    # Webhook Settings
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    webhook_secret: Optional[str] = Field(None, description="Webhook authentication secret")
    
    # Status Settings
    is_primary: bool = Field(False, description="Set as primary PBX")
    auto_assign_calls: bool = Field(True, description="Auto-assign incoming calls")

class PBXProviderUpdate(BaseModel):
    """Schema for updating a PBX provider"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    context: Optional[str] = None
    caller_id_field: Optional[str] = None
    dialplan_context: Optional[str] = None
    recording_enabled: Optional[bool] = None
    recording_path: Optional[str] = None
    transcription_enabled: Optional[bool] = None
    cdr_enabled: Optional[bool] = None
    cdr_path: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_primary: Optional[bool] = None
    auto_assign_calls: Optional[bool] = None
    is_active: Optional[bool] = None

class PBXProviderResponse(BaseModel):
    """Schema for PBX provider response"""
    id: int
    organization_id: int
    name: str
    provider_type: str
    display_name: str
    description: Optional[str]
    host: str
    port: int
    username: str
    # password: str  # Don't expose password in response
    # api_key: str  # Don't expose API key in response
    context: str
    caller_id_field: str
    dialplan_context: str
    recording_enabled: bool
    recording_path: str
    transcription_enabled: bool
    cdr_enabled: bool
    cdr_path: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]
    is_active: bool
    is_primary: bool
    auto_assign_calls: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime]
    
    class Config:
        from_attributes = True

# PBX Extension Schemas
class PBXExtensionCreate(BaseModel):
    """Schema for creating a PBX extension"""
    provider_id: int = Field(..., description="PBX provider ID")
    user_id: Optional[int] = Field(None, description="Associated user ID (null for system extensions)")
    extension_number: str = Field(..., description="Extension number (e.g., '1001')")
    extension_name: str = Field(..., description="Extension name")
    extension_type: ExtensionType = Field(ExtensionType.USER, description="Extension type")
    
    # Technical Settings
    device_type: Optional[str] = Field(None, description="Device type: sip, pjsip, iax, dahdi")
    device_config: Optional[Dict[str, Any]] = Field(None, description="Device-specific configuration")
    voicemail_enabled: bool = Field(True, description="Enable voicemail")
    voicemail_password: Optional[str] = Field(None, description="Voicemail password")
    
    # Call Handling
    ring_timeout: int = Field(30, description="Ring timeout in seconds")
    max_ring_timeout: int = Field(60, description="Maximum ring time in seconds")
    call_forward_enabled: bool = Field(False, description="Enable call forwarding")
    call_forward_number: Optional[str] = Field(None, description="Forward to number")
    call_forward_conditions: Optional[Dict[str, Any]] = Field(None, description="Forward conditions")
    
    # Presence and Status
    presence_status: PresenceStatus = Field(PresenceStatus.AVAILABLE, description="Presence status")
    dnd_enabled: bool = Field(False, description="Do Not Disturb enabled")
    auto_answer: bool = Field(False, description="Auto-answer calls")
    
    # Queue Settings (for queue extensions)
    queue_strategy: Optional[QueueStrategy] = Field(None, description="Queue strategy")
    queue_timeout: Optional[int] = Field(None, description="Queue timeout")
    queue_retry: Optional[int] = Field(None, description="Queue retry count")
    queue_wrapup_time: Optional[int] = Field(None, description="Wrap-up time")

class PBXExtensionUpdate(BaseModel):
    """Schema for updating a PBX extension"""
    extension_name: Optional[str] = None
    extension_type: Optional[ExtensionType] = None
    device_type: Optional[str] = None
    device_config: Optional[Dict[str, Any]] = None
    voicemail_enabled: Optional[bool] = None
    voicemail_password: Optional[str] = None
    ring_timeout: Optional[int] = None
    max_ring_timeout: Optional[int] = None
    call_forward_enabled: Optional[bool] = None
    call_forward_number: Optional[str] = None
    call_forward_conditions: Optional[Dict[str, Any]] = None
    presence_status: Optional[PresenceStatus] = None
    dnd_enabled: Optional[bool] = None
    auto_answer: Optional[bool] = None
    queue_strategy: Optional[QueueStrategy] = None
    queue_timeout: Optional[int] = None
    queue_retry: Optional[int] = None
    queue_wrapup_time: Optional[int] = None
    is_active: Optional[bool] = None

class PBXExtensionResponse(BaseModel):
    """Schema for PBX extension response"""
    id: int
    provider_id: int
    organization_id: int
    user_id: Optional[int]
    extension_number: str
    extension_name: str
    extension_type: str
    device_type: Optional[str]
    device_config: Optional[Dict[str, Any]]
    voicemail_enabled: bool
    voicemail_password: Optional[str]
    ring_timeout: int
    max_ring_timeout: int
    call_forward_enabled: bool
    call_forward_number: Optional[str]
    call_forward_conditions: Optional[Dict[str, Any]]
    presence_status: str
    dnd_enabled: bool
    auto_answer: bool
    queue_strategy: Optional[str]
    queue_timeout: Optional[int]
    queue_retry: Optional[int]
    queue_wrapup_time: Optional[int]
    is_active: bool
    is_registered: bool
    last_registered: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Call Schemas
class CallCreate(BaseModel):
    """Schema for creating a call record"""
    provider_id: int = Field(..., description="PBX provider ID")
    extension_id: Optional[int] = Field(None, description="Extension ID")
    unique_id: str = Field(..., description="PBX unique call ID")
    pbx_call_id: Optional[str] = Field(None, description="PBX-specific call identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Call Details
    caller_id: str = Field(..., description="Calling number")
    caller_name: Optional[str] = Field(None, description="Caller ID name")
    called_number: str = Field(..., description="Called number")
    called_name: Optional[str] = Field(None, description="Called party name")
    
    # Call Direction and Type
    direction: CallDirection = Field(..., description="Call direction")
    call_type: str = Field("voice", description="Call type: voice, video, conference")
    
    # Contact Association
    contact_id: Optional[int] = Field(None, description="Associated contact ID")
    lead_id: Optional[int] = Field(None, description="Associated lead ID")
    deal_id: Optional[int] = Field(None, description="Associated deal ID")
    
    # Agent Assignment
    agent_id: Optional[int] = Field(None, description="Assigned agent ID")
    queue_id: Optional[int] = Field(None, description="Queue ID")
    
    # Call Status and Timing
    status: CallStatus = Field(..., description="Call status")
    start_time: datetime = Field(..., description="Call start time")
    answer_time: Optional[datetime] = Field(None, description="Call answer time")
    end_time: Optional[datetime] = Field(None, description="Call end time")
    duration: int = Field(0, description="Duration in seconds")
    talk_time: int = Field(0, description="Talk time in seconds")
    hold_time: int = Field(0, description="Hold time in seconds")
    wait_time: int = Field(0, description="Wait time in queue")

class CallUpdate(BaseModel):
    """Schema for updating a call record"""
    caller_name: Optional[str] = None
    called_name: Optional[str] = None
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    agent_id: Optional[int] = None
    queue_id: Optional[int] = None
    status: Optional[CallStatus] = None
    answer_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    talk_time: Optional[int] = None
    hold_time: Optional[int] = None
    wait_time: Optional[int] = None
    quality_score: Optional[float] = None
    recording_url: Optional[str] = None
    recording_duration: Optional[int] = None
    transcription_url: Optional[str] = None
    transcription_text: Optional[str] = None
    disposition: Optional[CallDisposition] = None
    hangup_cause: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[float] = None
    cost_currency: Optional[str] = None
    cdr_data: Optional[Dict[str, Any]] = None

class CallResponse(BaseModel):
    """Schema for call response"""
    id: int
    organization_id: int
    provider_id: int
    extension_id: Optional[int]
    unique_id: str
    pbx_call_id: Optional[str]
    session_id: Optional[str]
    caller_id: str
    caller_name: Optional[str]
    called_number: str
    called_name: Optional[str]
    direction: str
    call_type: str
    contact_id: Optional[int]
    lead_id: Optional[int]
    deal_id: Optional[int]
    agent_id: Optional[int]
    queue_id: Optional[int]
    status: str
    start_time: datetime
    answer_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: int
    talk_time: int
    hold_time: int
    wait_time: int
    quality_score: Optional[float]
    recording_url: Optional[str]
    recording_duration: Optional[int]
    transcription_url: Optional[str]
    transcription_text: Optional[str]
    disposition: Optional[str]
    hangup_cause: Optional[str]
    notes: Optional[str]
    cost: float
    cost_currency: str
    cdr_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Call Queue Schemas
class CallQueueCreate(BaseModel):
    """Schema for creating a call queue"""
    provider_id: int = Field(..., description="PBX provider ID")
    name: str = Field(..., description="Queue name")
    description: Optional[str] = Field(None, description="Queue description")
    queue_number: str = Field(..., description="Queue extension number")
    
    # Queue Strategy
    strategy: QueueStrategy = Field(QueueStrategy.RINGALL, description="Queue strategy")
    timeout: int = Field(30, description="Ring timeout in seconds")
    retry: int = Field(5, description="Number of retries")
    wrapup_time: int = Field(30, description="Wrap-up time in seconds")
    max_wait_time: int = Field(300, description="Maximum wait time in queue")
    
    # Queue Settings
    music_on_hold: str = Field("default", description="Music on hold class")
    announce_frequency: int = Field(30, description="Announcement frequency in seconds")
    announce_position: bool = Field(True, description="Announce queue position")
    announce_hold_time: bool = Field(True, description="Announce estimated hold time")
    
    # Queue Members
    max_calls_per_agent: int = Field(1, description="Max calls per agent")
    join_empty: bool = Field(True, description="Join queue when no agents available")
    leave_when_empty: bool = Field(False, description="Leave queue when no callers")
    
    # Priority and Routing
    priority: int = Field(0, description="Queue priority")
    skill_based_routing: bool = Field(False, description="Enable skill-based routing")
    required_skills: Optional[List[str]] = Field(None, description="Required skills")

class CallQueueUpdate(BaseModel):
    """Schema for updating a call queue"""
    name: Optional[str] = None
    description: Optional[str] = None
    queue_number: Optional[str] = None
    strategy: Optional[QueueStrategy] = None
    timeout: Optional[int] = None
    retry: Optional[int] = None
    wrapup_time: Optional[int] = None
    max_wait_time: Optional[int] = None
    music_on_hold: Optional[str] = None
    announce_frequency: Optional[int] = None
    announce_position: Optional[bool] = None
    announce_hold_time: Optional[bool] = None
    max_calls_per_agent: Optional[int] = None
    join_empty: Optional[bool] = None
    leave_when_empty: Optional[bool] = None
    priority: Optional[int] = None
    skill_based_routing: Optional[bool] = None
    required_skills: Optional[List[str]] = None
    is_active: Optional[bool] = None

class CallQueueResponse(BaseModel):
    """Schema for call queue response"""
    id: int
    organization_id: int
    provider_id: int
    name: str
    description: Optional[str]
    queue_number: str
    strategy: str
    timeout: int
    retry: int
    wrapup_time: int
    max_wait_time: int
    music_on_hold: str
    announce_frequency: int
    announce_position: bool
    announce_hold_time: bool
    max_calls_per_agent: int
    join_empty: bool
    leave_when_empty: bool
    priority: int
    skill_based_routing: bool
    required_skills: Optional[List[str]]
    is_active: bool
    current_calls: int
    current_agents: int
    total_calls: int
    answered_calls: int
    abandoned_calls: int
    avg_wait_time: float
    avg_talk_time: float
    service_level: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Call Queue Member Schemas
class CallQueueMemberCreate(BaseModel):
    """Schema for adding a member to a call queue"""
    queue_id: int = Field(..., description="Queue ID")
    user_id: int = Field(..., description="User ID")
    extension_number: str = Field(..., description="Extension number")
    member_name: str = Field(..., description="Member name")
    penalty: int = Field(0, description="Penalty (lower = higher priority)")
    paused: bool = Field(False, description="Paused from queue")
    paused_reason: Optional[str] = Field(None, description="Reason for pause")
    skills: Optional[Dict[str, int]] = Field(None, description="Skills and proficiency levels")

class CallQueueMemberUpdate(BaseModel):
    """Schema for updating a queue member"""
    extension_number: Optional[str] = None
    member_name: Optional[str] = None
    penalty: Optional[int] = None
    paused: Optional[bool] = None
    paused_reason: Optional[str] = None
    skills: Optional[Dict[str, int]] = None
    status: Optional[AgentStatus] = None

class CallQueueMemberResponse(BaseModel):
    """Schema for call queue member response"""
    id: int
    queue_id: int
    user_id: int
    extension_number: str
    member_name: str
    penalty: int
    paused: bool
    paused_reason: Optional[str]
    skills: Optional[Dict[str, int]]
    status: str
    last_status_change: Optional[datetime]
    total_calls: int
    answered_calls: int
    missed_calls: int
    avg_talk_time: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Call Campaign Schemas
class CallCampaignCreate(BaseModel):
    """Schema for creating a call campaign"""
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    campaign_type: CampaignType = Field(CampaignType.OUTBOUND, description="Campaign type")
    
    # Target Settings
    target_contacts: Optional[List[int]] = Field(None, description="Target contact IDs")
    target_leads: Optional[List[int]] = Field(None, description="Target lead IDs")
    target_segments: Optional[List[int]] = Field(None, description="Target segment IDs")
    
    # Campaign Settings
    max_concurrent_calls: int = Field(5, description="Max concurrent calls")
    call_timeout: int = Field(30, description="Call timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_interval: int = Field(3600, description="Retry interval in seconds")
    
    # Scheduling
    start_time: Optional[datetime] = Field(None, description="Campaign start time")
    end_time: Optional[datetime] = Field(None, description="Campaign end time")
    business_hours_only: bool = Field(True, description="Only call during business hours")
    business_hours_start: str = Field("09:00", description="Business hours start")
    business_hours_end: str = Field("17:00", description="Business hours end")
    business_days: List[str] = Field(["monday", "tuesday", "wednesday", "thursday", "friday"], description="Business days")
    timezone: str = Field("UTC", description="Timezone")
    
    # Call Script and Settings
    script_template: Optional[str] = Field(None, description="Call script template")
    recording_enabled: bool = Field(True, description="Enable call recording")
    transcription_enabled: bool = Field(False, description="Enable transcription")

class CallCampaignUpdate(BaseModel):
    """Schema for updating a call campaign"""
    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[CampaignType] = None
    target_contacts: Optional[List[int]] = None
    target_leads: Optional[List[int]] = None
    target_segments: Optional[List[int]] = None
    max_concurrent_calls: Optional[int] = None
    call_timeout: Optional[int] = None
    retry_attempts: Optional[int] = None
    retry_interval: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    business_hours_only: Optional[bool] = None
    business_hours_start: Optional[str] = None
    business_hours_end: Optional[str] = None
    business_days: Optional[List[str]] = None
    timezone: Optional[str] = None
    script_template: Optional[str] = None
    recording_enabled: Optional[bool] = None
    transcription_enabled: Optional[bool] = None
    status: Optional[CampaignStatus] = None

class CallCampaignResponse(BaseModel):
    """Schema for call campaign response"""
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    campaign_type: str
    target_contacts: Optional[List[int]]
    target_leads: Optional[List[int]]
    target_segments: Optional[List[int]]
    max_concurrent_calls: int
    call_timeout: int
    retry_attempts: int
    retry_interval: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    business_hours_only: bool
    business_hours_start: str
    business_hours_end: str
    business_days: List[str]
    timezone: str
    script_template: Optional[str]
    recording_enabled: bool
    transcription_enabled: bool
    status: str
    progress: Optional[Dict[str, Any]]
    total_targets: int
    calls_made: int
    calls_answered: int
    calls_completed: int
    success_rate: float
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Call Analytics Schemas
class CallAnalyticsResponse(BaseModel):
    """Schema for call analytics response"""
    id: int
    organization_id: int
    period_type: str
    period_start: datetime
    period_end: datetime
    total_calls: int
    inbound_calls: int
    outbound_calls: int
    internal_calls: int
    answered_calls: int
    missed_calls: int
    abandoned_calls: int
    answer_rate: float
    abandonment_rate: float
    avg_call_duration: float
    avg_talk_time: float
    avg_wait_time: float
    avg_hold_time: float
    queue_calls: int
    queue_answered: int
    queue_abandoned: int
    service_level: float
    avg_queue_wait: float
    active_agents: int
    total_agent_time: int
    avg_agent_utilization: float
    total_cost: float
    avg_cost_per_call: float
    avg_quality_score: float
    recordings_count: int
    transcriptions_count: int
    queue_breakdown: Optional[Dict[str, Any]]
    agent_breakdown: Optional[Dict[str, Any]]
    hourly_breakdown: Optional[Dict[str, Any]]
    trends: Optional[Dict[str, Any]]
    insights: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard and Real-time Schemas
class CallCenterDashboard(BaseModel):
    """Schema for call center dashboard data"""
    active_calls: int
    queued_calls: int
    available_agents: int
    busy_agents: int
    offline_agents: int
    current_queue_status: List[Dict[str, Any]]
    recent_calls: List[CallResponse]
    agent_status: List[Dict[str, Any]]
    queue_metrics: List[Dict[str, Any]]
    hourly_stats: Dict[str, Any]
    daily_stats: Dict[str, Any]
    alerts: List[Dict[str, Any]]

class RealTimeCallUpdate(BaseModel):
    """Schema for real-time call updates"""
    call_id: int
    unique_id: str
    status: str
    timestamp: datetime
    agent_id: Optional[int]
    queue_id: Optional[int]
    duration: Optional[int]
    talk_time: Optional[int]
    hold_time: Optional[int]
    wait_time: Optional[int]
    data: Optional[Dict[str, Any]]

class CallTransferRequest(BaseModel):
    """Schema for call transfer request"""
    call_id: int
    target_extension: str
    target_type: str = Field(..., description="Extension type: user, queue, external")
    transfer_type: str = Field("blind", description="Transfer type: blind, attended")
    notes: Optional[str] = None

class CallHoldRequest(BaseModel):
    """Schema for call hold request"""
    call_id: int
    hold: bool = Field(..., description="True to hold, False to unhold")
    reason: Optional[str] = None

class CallMuteRequest(BaseModel):
    """Schema for call mute request"""
    call_id: int
    mute: bool = Field(..., description="True to mute, False to unmute")

class CallRecordingRequest(BaseModel):
    """Schema for call recording request"""
    call_id: int
    start_recording: bool = Field(..., description="True to start, False to stop")
    format: str = Field("wav", description="Recording format: wav, mp3, etc.")

class CallConferenceRequest(BaseModel):
    """Schema for call conference request"""
    call_id: int
    action: str = Field(..., description="Action: create, join, leave, add_participant")
    conference_id: Optional[str] = None
    participant_extension: Optional[str] = None
