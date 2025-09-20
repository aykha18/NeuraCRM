from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanySettingsCreate(BaseModel):
    """Request schema for creating company settings"""
    company_name: str
    company_mobile: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    complete_address: Optional[str] = None
    trn: Optional[str] = None
    currency: str = "AED - UAE Dirham (د.إ)"
    timezone: str = "Dubai (UAE)"
    
    # Billing Configuration
    trial_date_enabled: bool = True
    trial_date_days: int = 3
    delivery_date_enabled: bool = True
    delivery_date_days: int = 3
    advance_payment_enabled: bool = True

class CompanySettingsUpdate(BaseModel):
    """Request schema for updating company settings"""
    company_name: Optional[str] = None
    company_mobile: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    complete_address: Optional[str] = None
    trn: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    
    # Billing Configuration
    trial_date_enabled: Optional[bool] = None
    trial_date_days: Optional[int] = None
    delivery_date_enabled: Optional[bool] = None
    delivery_date_days: Optional[int] = None
    advance_payment_enabled: Optional[bool] = None

class CompanySettingsResponse(BaseModel):
    """Response schema for company settings"""
    id: int
    organization_id: int
    
    # Company Information
    company_name: str
    company_mobile: Optional[str]
    city: Optional[str]
    area: Optional[str]
    complete_address: Optional[str]
    trn: Optional[str]
    currency: str
    timezone: str
    
    # Billing Configuration
    trial_date_enabled: bool
    trial_date_days: int
    delivery_date_enabled: bool
    delivery_date_days: int
    advance_payment_enabled: bool
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: int
    
    class Config:
        from_attributes = True
