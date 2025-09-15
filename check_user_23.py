import os
import sys
sys.path.append('backend')

from backend.api.db import get_session_local
from backend.api.models import User

def check_user():
    try:
        db = get_session_local()()
        
        # Check if user 23 exists
        user = db.query(User).filter(User.id == 23).first()
        
        if user:
            print(f"User 23 found:")
            print(f"  ID: {user.id}")
            print(f"  Name: {user.name}")
            print(f"  Email: {user.email}")
            print(f"  Organization ID: {user.organization_id}")
            print(f"  Role: {user.role}")
        else:
            print("User 23 not found")
            
        # List all users
        all_users = db.query(User).all()
        print(f"\nAll users in database ({len(all_users)} total):")
        for u in all_users:
            print(f"  ID: {u.id}, Name: {u.name}, Email: {u.email}, Org: {u.organization_id}")
        
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user()
