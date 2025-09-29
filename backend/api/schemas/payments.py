"""
Pydantic schemas for payment-related operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"

class PaymentMethodType(str, Enum):
    CARD = "card"
    BANK_ACCOUNT = "bank_account"

# Payment Method Schemas
class PaymentMethodBase(BaseModel):
    type: PaymentMethodType
    brand: Optional[str] = None
    last4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False

class PaymentMethodCreate(PaymentMethodBase):
    stripe_payment_method_id: str
    customer_id: int

class PaymentMethodUpdate(BaseModel):
    is_default: Optional[bool] = None

class PaymentMethodResponse(PaymentMethodBase):
    id: int
    stripe_payment_method_id: str
    customer_id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Payment Schemas
class StripePaymentBase(BaseModel):
    amount: float = Field(..., description="Amount in cents")
    currency: str = Field(default="usd")
    payment_metadata: Optional[Dict[str, Any]] = None

class PaymentCreate(StripePaymentBase):
    invoice_id: Optional[int] = None
    subscription_id: Optional[int] = None
    customer_id: int
    payment_method_id: Optional[int] = None

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    failure_reason: Optional[str] = None

class PaymentResponse(StripePaymentBase):
    id: int
    stripe_payment_intent_id: str
    invoice_id: Optional[int]
    subscription_id: Optional[int]
    customer_id: int
    organization_id: int
    status: PaymentStatus
    payment_method_id: Optional[int]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Subscription Plan Schemas
class SubscriptionPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float = Field(..., description="Amount in cents")
    currency: str = Field(default="usd")
    interval: str = Field(..., description="billing interval (month, year)")
    interval_count: int = Field(default=1)
    trial_period_days: int = Field(default=0)
    features: Optional[List[str]] = None
    is_active: bool = True

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    interval: Optional[str] = None
    interval_count: Optional[int] = None
    trial_period_days: Optional[int] = None
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None

class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int
    stripe_price_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    customer_id: int
    plan_id: int
    payment_metadata: Optional[Dict[str, Any]] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    status: Optional[SubscriptionStatus] = None
    cancel_at_period_end: Optional[bool] = None
    payment_metadata: Optional[Dict[str, Any]] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    stripe_subscription_id: str
    organization_id: int
    status: SubscriptionStatus
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Payment Intent Schemas
class PaymentIntentCreate(BaseModel):
    amount: float = Field(..., description="Amount in cents")
    currency: str = Field(default="usd")
    customer_id: int
    payment_method_id: str
    invoice_id: Optional[int] = None
    payment_metadata: Optional[Dict[str, Any]] = None

class PaymentIntentResponse(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    client_secret: str
    payment_metadata: Dict[str, Any]

# Webhook Schemas
class StripeWebhookEvent(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]
    created: int

# Analytics Schemas
class PaymentAnalytics(BaseModel):
    total_revenue: float
    total_payments: int
    successful_payments: int
    failed_payments: int
    success_rate: float
    average_payment_amount: float
    payments_by_status: Dict[str, int]
    payments_by_month: Dict[str, int]

class SubscriptionAnalytics(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    canceled_subscriptions: int
    churn_rate: float
    monthly_recurring_revenue: float
    subscriptions_by_status: Dict[str, int]
    subscriptions_by_plan: Dict[str, int]

# Dashboard Schemas
class PaymentDashboard(BaseModel):
    recent_payments: List[PaymentResponse]
    failed_payments: List[PaymentResponse]
    pending_payments: List[PaymentResponse]
    analytics: PaymentAnalytics

class SubscriptionDashboard(BaseModel):
    active_subscriptions: List[SubscriptionResponse]
    upcoming_renewals: List[SubscriptionResponse]
    canceled_subscriptions: List[SubscriptionResponse]
    analytics: SubscriptionAnalytics
