from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class OrganizationSignupRequest(BaseModel):
    """Request schema for organization signup"""
    organization_name: str
    organization_domain: Optional[str] = None
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    plan: str = "free"  # free, pro, enterprise
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Organization name must be at least 2 characters')
        return v.strip()
    
    @validator('admin_name')
    def validate_admin_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Admin name must be at least 2 characters')
        return v.strip()
    
    @validator('admin_password')
    def validate_admin_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('plan')
    def validate_plan(cls, v):
        allowed_plans = ['free', 'pro', 'enterprise']
        if v not in allowed_plans:
            raise ValueError(f'Plan must be one of: {", ".join(allowed_plans)}')
        return v

class OrganizationSignupResponse(BaseModel):
    """Response schema for organization signup"""
    organization: dict
    admin_user: dict
    subscription: dict
    access_token: str
    token_type: str = "bearer"

class SubscriptionPlanResponse(BaseModel):
    """Response schema for subscription plans"""
    id: int
    name: str
    display_name: str
    description: str
    price_monthly: float
    price_yearly: float
    user_limit: int
    features: List[str]
    is_active: bool

class SubscriptionResponse(BaseModel):
    """Response schema for organization subscription"""
    id: int
    organization_id: int
    plan: str
    status: str
    billing_cycle: str
    user_limit: int
    features: dict
    created_at: datetime
    expires_at: Optional[datetime]
    trial_ends_at: Optional[datetime]

class OrganizationResponse(BaseModel):
    """Response schema for organization"""
    id: int
    name: str
    domain: Optional[str]
    created_at: datetime
    subscription: Optional[SubscriptionResponse]

class UserLimitCheck(BaseModel):
    """Response schema for user limit check"""
    current_users: int
    user_limit: int
    can_add_user: bool
    plan: str
