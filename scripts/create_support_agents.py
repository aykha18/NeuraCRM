#!/usr/bin/env python3
"""
Create support agents with proper roles for the assignment system
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.db import get_db
from api.models import User, Organization
import bcrypt

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_support_agents():
    """Create support agents with proper roles"""
    db = next(get_db())
    
    try:
        # Get organization (assuming org_id = 8 for nodeit@node.com)
        org = db.query(Organization).filter(Organization.id == 8).first()
        if not org:
            print("Organization not found. Please run the main seed script first.")
            return
        
        # Check existing users
        existing_users = db.query(User).filter(User.organization_id == org.id).all()
        print(f"Found {len(existing_users)} existing users in organization {org.id}")
        
        # Update existing users to have proper roles if they don't
        for user in existing_users:
            if not user.role or user.role not in ['agent', 'manager', 'admin']:
                # Assign roles based on email or name patterns
                if 'admin' in user.email.lower() or 'manager' in user.name.lower():
                    user.role = 'manager'
                else:
                    user.role = 'agent'
                print(f"Updated {user.name} ({user.email}) role to: {user.role}")
        
        # Create additional support agents if needed
        support_agents = [
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@nodeit.com',
                'role': 'agent',
                'password': 'SupportAgent2024!'
            },
            {
                'name': 'Mike Chen',
                'email': 'mike.chen@nodeit.com', 
                'role': 'agent',
                'password': 'SupportAgent2024!'
            },
            {
                'name': 'Lisa Rodriguez',
                'email': 'lisa.rodriguez@nodeit.com',
                'role': 'manager',
                'password': 'SupportManager2024!'
            },
            {
                'name': 'David Kim',
                'email': 'david.kim@nodeit.com',
                'role': 'agent',
                'password': 'SupportAgent2024!'
            }
        ]
        
        for agent_data in support_agents:
            # Check if user already exists
            existing_user = db.query(User).filter(
                User.email == agent_data['email'],
                User.organization_id == org.id
            ).first()
            
            if not existing_user:
                user = User(
                    name=agent_data['name'],
                    email=agent_data['email'],
                    password_hash=get_password_hash(agent_data['password']),
                    role=agent_data['role'],
                    organization_id=org.id,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                print(f"Created {agent_data['role']}: {agent_data['name']} ({agent_data['email']})")
            else:
                # Update role if needed
                if existing_user.role != agent_data['role']:
                    existing_user.role = agent_data['role']
                    print(f"Updated role for {existing_user.name} to: {agent_data['role']}")
        
        db.commit()
        
        # Show final agent count
        agents = db.query(User).filter(
            User.organization_id == org.id,
            User.role.in_(['agent', 'manager', 'admin'])
        ).all()
        
        print(f"\n✅ Support agents created/updated successfully!")
        print(f"Total agents available: {len(agents)}")
        for agent in agents:
            print(f"  - {agent.name} ({agent.email}) - {agent.role}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating support agents: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_support_agents()
