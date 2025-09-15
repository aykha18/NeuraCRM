#!/usr/bin/env python3
"""
Script to check for duplicate users with same email in different organizations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.api.db import get_session_local
from backend.api.models import User

def check_duplicate_users():
    """Check for users with duplicate emails"""
    db = get_session_local()()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        print(f"Total users in database: {len(users)}")
        print("\nAll users:")
        print("-" * 80)
        
        email_count = {}
        
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Name: {user.name}, Org: {user.organization_id}")
            
            # Count emails
            if user.email in email_count:
                email_count[user.email] += 1
            else:
                email_count[user.email] = 1
        
        print("\n" + "=" * 80)
        print("EMAIL DUPLICATE ANALYSIS:")
        print("=" * 80)
        
        duplicates_found = False
        for email, count in email_count.items():
            if count > 1:
                duplicates_found = True
                print(f"❌ DUPLICATE: {email} appears {count} times")
                
                # Show all users with this email
                duplicate_users = [u for u in users if u.email == email]
                for user in duplicate_users:
                    print(f"   - User ID {user.id}, Org {user.organization_id}, Name: {user.name}")
        
        if not duplicates_found:
            print("✅ No duplicate emails found")
        
        # Check specifically for nodeit@node.com
        print("\n" + "=" * 80)
        print("NODEIT@NODE.COM ANALYSIS:")
        print("=" * 80)
        
        nodeit_users = db.query(User).filter(User.email == "nodeit@node.com").all()
        print(f"Users with email 'nodeit@node.com': {len(nodeit_users)}")
        
        for user in nodeit_users:
            print(f"  - User ID: {user.id}")
            print(f"    Name: {user.name}")
            print(f"    Organization ID: {user.organization_id}")
            print(f"    Role: {user.role}")
            print(f"    Created: {user.created_at}")
            print()
        
    finally:
        db.close()

if __name__ == "__main__":
    check_duplicate_users()
