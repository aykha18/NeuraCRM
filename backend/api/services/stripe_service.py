"""
Stripe Payment Gateway Service
Handles all Stripe-related operations for payments, subscriptions, and customer management
"""

import stripe
import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from api.models import PaymentMethod, StripePayment, StripeSubscription, StripeSubscriptionPlan, Contact, Invoice

logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        # Initialize Stripe with API key
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY not found in environment variables")
        
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    async def create_customer(self, contact: Contact, organization_id: int) -> Optional[str]:
        """Create a Stripe customer for a contact"""
        try:
            customer = stripe.Customer.create(
                email=contact.email,
                name=contact.name,
                phone=contact.phone,
                metadata={
                    'contact_id': str(contact.id),
                    'organization_id': str(organization_id),
                    'company': contact.company or ''
                }
            )
            logger.info(f"Created Stripe customer: {customer.id} for contact: {contact.id}")
            return customer.id
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {str(e)}")
            return None
    
    async def create_payment_method(self, customer_id: str, payment_method_id: str, 
                                  contact_id: int, organization_id: int) -> Optional[PaymentMethod]:
        """Attach a payment method to a customer"""
        try:
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            
            # Retrieve payment method details
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Create database record
            db_payment_method = PaymentMethod(
                stripe_payment_method_id=payment_method_id,
                customer_id=contact_id,
                organization_id=organization_id,
                type=pm.type,
                brand=pm.card.brand if pm.card else None,
                last4=pm.card.last4 if pm.card else None,
                exp_month=pm.card.exp_month if pm.card else None,
                exp_year=pm.card.exp_year if pm.card else None,
                is_default=False  # Will be set to True if this is the first payment method
            )
            
            logger.info(f"Created payment method: {payment_method_id}")
            return db_payment_method
            
        except Exception as e:
            logger.error(f"Error creating payment method: {str(e)}")
            return None
    
    async def create_payment_intent(self, amount: int, currency: str, customer_id: str,
                                  payment_method_id: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a payment intent for one-time payments"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                payment_metadata=metadata or {}
            )
            
            logger.info(f"Created payment intent: {intent.id}")
            return intent.id
            
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            return None
    
    async def process_invoice_payment(self, invoice: Invoice, payment_method_id: str, 
                                    db: Session) -> Optional[StripePayment]:
        """Process payment for an invoice"""
        try:
            # Get customer's Stripe customer ID
            contact = invoice.contact
            customer_id = await self.get_or_create_customer(contact, db)
            
            if not customer_id:
                logger.error(f"Could not get/create Stripe customer for contact: {contact.id}")
                return None
            
            # Create payment intent
            intent_id = await self.create_payment_intent(
                amount=int(invoice.amount * 100),  # Convert to cents
                currency='usd',
                customer_id=customer_id,
                payment_method_id=payment_method_id,
                metadata={
                    'invoice_id': str(invoice.id),
                    'contact_id': str(contact.id),
                    'organization_id': str(contact.organization_id)
                }
            )
            
            if not intent_id:
                return None
            
            # Retrieve payment intent to get status
            intent = stripe.PaymentIntent.retrieve(intent_id)
            
            # Create payment record
            payment = StripePayment(
                stripe_payment_intent_id=intent_id,
                invoice_id=invoice.id,
                customer_id=contact.id,
                organization_id=contact.organization_id,
                amount=intent.amount,
                currency=intent.currency,
                status=intent.status,
                payment_method_id=None,  # Will be set if payment method exists in DB
                payment_metadata=intent.metadata
            )
            
            # Update invoice status if payment succeeded
            if intent.status == 'succeeded':
                invoice.status = 'paid'
                payment.status = 'succeeded'
            elif intent.status == 'requires_action':
                payment.status = 'pending'
            else:
                payment.status = 'failed'
                payment.failure_reason = intent.last_payment_error.message if intent.last_payment_error else 'Unknown error'
            
            db.add(payment)
            db.commit()
            
            logger.info(f"Processed invoice payment: {intent_id}")
            return payment
            
        except Exception as e:
            logger.error(f"Error processing invoice payment: {str(e)}")
            return None
    
    async def create_subscription(self, customer_id: str, price_id: str, 
                                trial_period_days: int = 0) -> Optional[str]:
        """Create a subscription for a customer"""
        try:
            subscription_params = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'payment_settings': {'save_default_payment_method': 'on_subscription'},
                'expand': ['latest_invoice.payment_intent'],
            }
            
            if trial_period_days > 0:
                subscription_params['trial_period_days'] = trial_period_days
            
            subscription = stripe.Subscription.create(**subscription_params)
            
            logger.info(f"Created subscription: {subscription.id}")
            return subscription.id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return None
    
    async def get_or_create_customer(self, contact: Contact, db: Session) -> Optional[str]:
        """Get existing Stripe customer ID or create new one"""
        try:
            # Check if contact already has a Stripe customer ID stored
            # For now, we'll create a new customer each time
            # In production, you'd store the Stripe customer ID in the contact record
            
            customer_id = await self.create_customer(contact, contact.organization_id)
            return customer_id
            
        except Exception as e:
            logger.error(f"Error getting/creating customer: {str(e)}")
            return None
    
    async def handle_webhook(self, payload: str, signature: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            if not self.webhook_secret:
                logger.error("Stripe webhook secret not configured")
                return False
            
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'payment_intent.succeeded':
                await self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                await self._handle_payment_failed(event['data']['object'])
            elif event['type'] == 'invoice.payment_succeeded':
                await self._handle_invoice_payment_succeeded(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                await self._handle_subscription_updated(event['data']['object'])
            
            logger.info(f"Handled webhook event: {event['type']}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return False
    
    async def _handle_payment_succeeded(self, payment_intent: Dict[str, Any]):
        """Handle successful payment"""
        # Update payment status in database
        logger.info(f"Payment succeeded: {payment_intent['id']}")
    
    async def _handle_payment_failed(self, payment_intent: Dict[str, Any]):
        """Handle failed payment"""
        # Update payment status and notify customer
        logger.info(f"Payment failed: {payment_intent['id']}")
    
    async def _handle_invoice_payment_succeeded(self, invoice: Dict[str, Any]):
        """Handle successful invoice payment"""
        # Update invoice status
        logger.info(f"Invoice payment succeeded: {invoice['id']}")
    
    async def _handle_subscription_updated(self, subscription: Dict[str, Any]):
        """Handle subscription updates"""
        # Update subscription status
        logger.info(f"Subscription updated: {subscription['id']}")
    
    async def create_subscription_plan(self, name: str, amount: int, currency: str,
                                     interval: str, description: str = None) -> Optional[str]:
        """Create a subscription plan in Stripe"""
        try:
            price = stripe.Price.create(
                unit_amount=amount,
                currency=currency,
                recurring={'interval': interval},
                product_data={
                    'name': name,
                    'description': description or ''
                }
            )
            
            logger.info(f"Created subscription plan: {price.id}")
            return price.id
            
        except Exception as e:
            logger.error(f"Error creating subscription plan: {str(e)}")
            return None
    
    async def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all payment methods for a customer"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            return payment_methods.data
            
        except Exception as e:
            logger.error(f"Error getting payment methods: {str(e)}")
            return []
    
    async def delete_payment_method(self, payment_method_id: str) -> bool:
        """Delete a payment method"""
        try:
            stripe.PaymentMethod.detach(payment_method_id)
            logger.info(f"Deleted payment method: {payment_method_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting payment method: {str(e)}")
            return False

# Initialize service
stripe_service = StripeService()
