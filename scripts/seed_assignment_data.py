#!/usr/bin/env python3
"""
Seed script for Support Assignment features
Creates sample support queues, user skills, and assignment data
"""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.db import get_db
from api.models import SupportQueue, UserSkill, User, Organization

def seed_assignment_data():
    """Seed assignment-related data"""
    db = next(get_db())
    
    try:
        # Get organization (assuming org_id = 8 for nodeit@node.com)
        org = db.query(Organization).filter(Organization.id == 8).first()
        if not org:
            print("Organization not found. Please run the main seed script first.")
            return
        
        # Create support queues
        queues = [
            {
                'name': 'Technical Support',
                'description': 'Handles technical issues and bug reports',
                'auto_assign': True,
                'round_robin': True,
                'max_workload': 8,
                'business_hours_only': False,
                'handles_priorities': ['low', 'medium', 'high', 'urgent', 'critical']
            },
            {
                'name': 'Billing Support',
                'description': 'Handles billing and payment issues',
                'auto_assign': True,
                'round_robin': True,
                'max_workload': 6,
                'business_hours_only': True,
                'business_hours_start': '09:00',
                'business_hours_end': '17:00',
                'handles_priorities': ['medium', 'high', 'urgent']
            },
            {
                'name': 'Tier 2 Support',
                'description': 'Senior support for complex issues',
                'auto_assign': False,
                'round_robin': False,
                'max_workload': 5,
                'business_hours_only': False,
                'handles_priorities': ['high', 'urgent', 'critical']
            }
        ]
        
        for queue_data in queues:
            existing_queue = db.query(SupportQueue).filter(
                SupportQueue.name == queue_data['name'],
                SupportQueue.organization_id == org.id
            ).first()
            
            if not existing_queue:
                queue = SupportQueue(
                    organization_id=org.id,
                    **queue_data
                )
                db.add(queue)
                print(f"Created queue: {queue_data['name']}")
            else:
                print(f"Queue already exists: {queue_data['name']}")
        
        # Get users to assign skills
        users = db.query(User).filter(User.organization_id == org.id).all()
        
        # Define skills for different roles
        skills_data = [
            # Technical skills
            {'name': 'technical', 'category': 'technical', 'level': 'advanced'},
            {'name': 'api_integration', 'category': 'technical', 'level': 'intermediate'},
            {'name': 'database', 'category': 'technical', 'level': 'advanced'},
            {'name': 'frontend', 'category': 'technical', 'level': 'intermediate'},
            {'name': 'backend', 'category': 'technical', 'level': 'advanced'},
            
            # Product skills
            {'name': 'billing', 'category': 'product', 'level': 'expert'},
            {'name': 'feature_request', 'category': 'product', 'level': 'intermediate'},
            {'name': 'user_experience', 'category': 'product', 'level': 'intermediate'},
            
            # General skills
            {'name': 'customer_service', 'category': 'general', 'level': 'expert'},
            {'name': 'troubleshooting', 'category': 'general', 'level': 'advanced'},
            {'name': 'documentation', 'category': 'general', 'level': 'intermediate'}
        ]
        
        # Assign skills to users based on their roles
        for user in users:
            user_skills = []
            
            if user.role == 'admin':
                # Admins get all skills
                user_skills = skills_data
            elif user.role == 'manager':
                # Managers get management and advanced technical skills
                user_skills = [
                    {'name': 'technical', 'category': 'technical', 'level': 'advanced'},
                    {'name': 'billing', 'category': 'product', 'level': 'expert'},
                    {'name': 'customer_service', 'category': 'general', 'level': 'expert'},
                    {'name': 'troubleshooting', 'category': 'general', 'level': 'advanced'},
                    {'name': 'user_experience', 'category': 'product', 'level': 'intermediate'}
                ]
            elif user.role == 'agent':
                # Agents get basic to intermediate skills
                user_skills = [
                    {'name': 'technical', 'category': 'technical', 'level': 'intermediate'},
                    {'name': 'customer_service', 'category': 'general', 'level': 'advanced'},
                    {'name': 'troubleshooting', 'category': 'general', 'level': 'intermediate'},
                    {'name': 'billing', 'category': 'product', 'level': 'intermediate'}
                ]
            
            # Create user skills
            for skill_data in user_skills:
                existing_skill = db.query(UserSkill).filter(
                    UserSkill.user_id == user.id,
                    UserSkill.skill_name == skill_data['name']
                ).first()
                
                if not existing_skill:
                    skill = UserSkill(
                        user_id=user.id,
                        skill_name=skill_data['name'],
                        skill_level=skill_data['level'],
                        category=skill_data['category'],
                        is_active=True
                    )
                    db.add(skill)
                    print(f"Added skill {skill_data['name']} ({skill_data['level']}) to {user.name}")
        
        db.commit()
        print("✅ Assignment data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding assignment data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_assignment_data()
