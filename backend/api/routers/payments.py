"""
Payment Gateway API Router
Handles all payment-related endpoints including Stripe integration
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from api.db import get_db
from api.models import PaymentMethod, StripePayment, StripeSubscription, StripeSubscriptionPlan, Contact, Invoice, User
from api.schemas.payments import (
    PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse,
    SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    PaymentIntentCreate, PaymentIntentResponse,
    PaymentAnalytics, SubscriptionAnalytics,
    PaymentDashboard, SubscriptionDashboard
)
from api.services.stripe_service import stripe_service
from api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])

# Payment Methods
@router.post("/payment-methods", response_model=PaymentMethodResponse)
async def create_payment_method(
    payment_method_data: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment method for a customer"""
    try:
        # Get the contact
        contact = db.query(Contact).filter(
            Contact.id == payment_method_data.customer_id,
            Contact.organization_id == current_user.organization_id
        ).first()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Create payment method in Stripe
        db_payment_method = await stripe_service.create_payment_method(
            customer_id="",  # Will be created if needed
            payment_method_id=payment_method_data.stripe_payment_method_id,
            contact_id=contact.id,
            organization_id=current_user.organization_id
        )
        
        if not db_payment_method:
            raise HTTPException(status_code=400, detail="Failed to create payment method")
        
        db.add(db_payment_method)
        db.commit()
        db.refresh(db_payment_method)
        
        logger.info(f"Created payment method: {db_payment_method.id}")
        return db_payment_method
        
    except Exception as e:
        logger.error(f"Error creating payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment methods for a customer or organization"""
    try:
        query = db.query(PaymentMethod).filter(
            PaymentMethod.organization_id == current_user.organization_id
        )
        
        if customer_id:
            query = query.filter(PaymentMethod.customer_id == customer_id)
        
        payment_methods = query.all()
        return payment_methods
        
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse)
async def update_payment_method(
    payment_method_id: int,
    payment_method_data: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a payment method"""
    try:
        payment_method = db.query(PaymentMethod).filter(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.organization_id == current_user.organization_id
        ).first()
        
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        # Update fields
        if payment_method_data.is_default is not None:
            # If setting as default, unset other defaults first
            if payment_method_data.is_default:
                db.query(PaymentMethod).filter(
                    PaymentMethod.organization_id == current_user.organization_id,
                    PaymentMethod.customer_id == payment_method.customer_id
                ).update({"is_default": False})
            
            payment_method.is_default = payment_method_data.is_default
        
        db.commit()
        db.refresh(payment_method)
        
        logger.info(f"Updated payment method: {payment_method_id}")
        return payment_method
        
    except Exception as e:
        logger.error(f"Error updating payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment method"""
    try:
        payment_method = db.query(PaymentMethod).filter(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.organization_id == current_user.organization_id
        ).first()
        
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        # Delete from Stripe
        success = await stripe_service.delete_payment_method(
            payment_method.stripe_payment_method_id
        )
        
        if success:
            db.delete(payment_method)
            db.commit()
            logger.info(f"Deleted payment method: {payment_method_id}")
            return {"message": "Payment method deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete payment method from Stripe")
        
    except Exception as e:
        logger.error(f"Error deleting payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Payments
@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment"""
    try:
        # Validate customer exists
        customer = db.query(Contact).filter(
            Contact.id == payment_data.customer_id,
            Contact.organization_id == current_user.organization_id
        ).first()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # If this is an invoice payment, process it
        if payment_data.invoice_id:
            invoice = db.query(Invoice).filter(
                Invoice.id == payment_data.invoice_id,
                Invoice.organization_id == current_user.organization_id
            ).first()
            
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            
            # Get payment method
            payment_method = db.query(PaymentMethod).filter(
                PaymentMethod.id == payment_data.payment_method_id,
                PaymentMethod.organization_id == current_user.organization_id
            ).first()
            
            if not payment_method:
                raise HTTPException(status_code=404, detail="Payment method not found")
            
            # Process the payment
            payment = await stripe_service.process_invoice_payment(
                invoice=invoice,
                payment_method_id=payment_method.stripe_payment_method_id,
                db=db
            )
            
            if not payment:
                raise HTTPException(status_code=400, detail="Failed to process payment")
            
            return payment
        
        # For non-invoice payments, create a simple payment record
        payment = StripePayment(
            stripe_payment_intent_id="",  # Will be set when processed
            customer_id=payment_data.customer_id,
            organization_id=current_user.organization_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status="pending",
            payment_metadata=payment_data.payment_metadata
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        logger.info(f"Created payment: {payment.id}")
        return payment
        
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payments with optional filtering"""
    try:
        query = db.query(StripePayment).filter(
            StripePayment.organization_id == current_user.organization_id
        )
        
        if customer_id:
            query = query.filter(StripePayment.customer_id == customer_id)
        
        if status:
            query = query.filter(StripePayment.status == status)
        
        payments = query.offset(offset).limit(limit).all()
        return payments
        
    except Exception as e:
        logger.error(f"Error getting payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Payment Intents
@router.post("/payment-intents", response_model=PaymentIntentResponse)
async def create_payment_intent(
    intent_data: PaymentIntentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a payment intent for frontend payment processing"""
    try:
        # Validate customer exists
        customer = db.query(Contact).filter(
            Contact.id == intent_data.customer_id,
            Contact.organization_id == current_user.organization_id
        ).first()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get or create Stripe customer
        stripe_customer_id = await stripe_service.get_or_create_customer(customer, db)
        
        if not stripe_customer_id:
            raise HTTPException(status_code=400, detail="Failed to create Stripe customer")
        
        # Create payment intent
        intent_id = await stripe_service.create_payment_intent(
            amount=int(intent_data.amount),
            currency=intent_data.currency,
            customer_id=stripe_customer_id,
            payment_method_id=intent_data.payment_method_id,
                payment_metadata=intent_data.payment_metadata or {}
        )
        
        if not intent_id:
            raise HTTPException(status_code=400, detail="Failed to create payment intent")
        
        # Retrieve the intent to get client secret
        import stripe
        intent = stripe.PaymentIntent.retrieve(intent_id)
        
        return PaymentIntentResponse(
            id=intent.id,
            amount=intent.amount,
            currency=intent.currency,
            status=intent.status,
            client_secret=intent.client_secret,
            payment_metadata=intent.payment_metadata
        )
        
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Subscription Plans
@router.post("/subscription-plans", response_model=SubscriptionPlanResponse)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subscription plan"""
    try:
        # Create plan in Stripe
        stripe_price_id = await stripe_service.create_subscription_plan(
            name=plan_data.name,
            amount=int(plan_data.amount),
            currency=plan_data.currency,
            interval=plan_data.interval,
            description=plan_data.description
        )
        
        if not stripe_price_id:
            raise HTTPException(status_code=400, detail="Failed to create plan in Stripe")
        
        # Create database record
        plan = StripeSubscriptionPlan(
            stripe_price_id=stripe_price_id,
            name=plan_data.name,
            description=plan_data.description,
            amount=plan_data.amount,
            currency=plan_data.currency,
            interval=plan_data.interval,
            interval_count=plan_data.interval_count,
            trial_period_days=plan_data.trial_period_days,
            features=plan_data.features,
            is_active=plan_data.is_active
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Created subscription plan: {plan.id}")
        return plan
        
    except Exception as e:
        logger.error(f"Error creating subscription plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subscription plans"""
    try:
        query = db.query(StripeSubscriptionPlan)
        
        if active_only:
            query = query.filter(StripeSubscriptionPlan.is_active == True)
        
        plans = query.all()
        return plans
        
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Analytics
@router.get("/analytics", response_model=PaymentAnalytics)
async def get_payment_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment analytics"""
    try:
        payments = db.query(StripePayment).filter(
            StripePayment.organization_id == current_user.organization_id
        ).all()
        
        total_payments = len(payments)
        successful_payments = len([p for p in payments if p.status == "succeeded"])
        failed_payments = len([p for p in payments if p.status == "failed"])
        
        total_revenue = sum(p.amount for p in payments if p.status == "succeeded")
        average_payment_amount = total_revenue / successful_payments if successful_payments > 0 else 0
        success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
        
        # Group by status
        payments_by_status = {}
        for payment in payments:
            status = payment.status
            payments_by_status[status] = payments_by_status.get(status, 0) + 1
        
        # Group by month (simplified)
        payments_by_month = {}
        for payment in payments:
            month_key = payment.created_at.strftime('%Y-%m')
            payments_by_month[month_key] = payments_by_month.get(month_key, 0) + 1
        
        return PaymentAnalytics(
            total_revenue=total_revenue,
            total_payments=total_payments,
            successful_payments=successful_payments,
            failed_payments=failed_payments,
            success_rate=success_rate,
            average_payment_amount=average_payment_amount,
            payments_by_status=payments_by_status,
            payments_by_month=payments_by_month
        )
        
    except Exception as e:
        logger.error(f"Error getting payment analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Webhook endpoint
@router.post("/webhooks/stripe")
async def stripe_webhook(
    payload: str,
    signature: str,
    background_tasks: BackgroundTasks
):
    """Handle Stripe webhook events"""
    try:
        success = await stripe_service.handle_webhook(payload, signature)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Webhook processing failed")
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
