#!/usr/bin/env python3
"""
Setup subscription plans for SaaS
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.db import get_db
from api.models import SubscriptionPlan
from sqlalchemy.orm import Session

def setup_subscription_plans():
    """Create default subscription plans"""
    db = next(get_db())
    
    # Define subscription plans
    plans = [
        {
            'name': 'free',
            'display_name': 'Free',
            'description': 'Perfect for small teams getting started',
            'price_monthly': 0.0,
            'price_yearly': 0.0,
            'user_limit': 5,
            'features': [
                'Up to 5 users',
                'Unlimited contacts & leads',
                'Basic pipeline management',
                'Email automation (100 emails/month)',
                'Basic reporting',
                'Mobile app access',
                'Email support'
            ]
        },
        {
            'name': 'pro',
            'display_name': 'Professional',
            'description': 'Advanced features for growing businesses',
            'price_monthly': 29.0,
            'price_yearly': 290.0,  # 2 months free
            'user_limit': 50,
            'features': [
                'Up to 50 users',
                'Everything in Free',
                'Advanced pipeline management',
                'Unlimited email automation',
                'Advanced reporting & analytics',
                'Custom fields & workflows',
                'API access',
                'Priority support',
                'Data export/import',
                'Custom branding'
            ]
        },
        {
            'name': 'enterprise',
            'display_name': 'Enterprise',
            'description': 'Full-featured solution for large organizations',
            'price_monthly': 99.0,
            'price_yearly': 990.0,  # 2 months free
            'user_limit': 1000,
            'features': [
                'Unlimited users',
                'Everything in Professional',
                'Advanced security & compliance',
                'SSO integration',
                'Custom integrations',
                'Dedicated account manager',
                '24/7 phone support',
                'Custom training',
                'SLA guarantee',
                'On-premise deployment option'
            ]
        }
    ]
    
    for plan_data in plans:
        # Check if plan already exists
        existing_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == plan_data['name']
        ).first()
        
        if existing_plan:
            print(f"Plan '{plan_data['name']}' already exists, updating...")
            for key, value in plan_data.items():
                setattr(existing_plan, key, value)
        else:
            print(f"Creating plan '{plan_data['name']}'...")
            plan = SubscriptionPlan(**plan_data)
            db.add(plan)
    
    db.commit()
    print("✅ Subscription plans setup completed!")
    
    # Display created plans
    print("\n📋 Available Plans:")
    for plan in db.query(SubscriptionPlan).all():
        print(f"  {plan.display_name} ({plan.name}): ${plan.price_monthly}/month, {plan.user_limit} users")

if __name__ == "__main__":
    setup_subscription_plans()
