#!/usr/bin/env python3
"""
Fix Railway Call Queue Members
=============================

Fixes the call queue members by using valid extension IDs from pbx_extensions.
"""

import psycopg2

import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta
import random

# Railway Database Configuration
# Railway DB config now loaded from environment variables

def fix_call_queue_members():
    """Fix call queue members with valid extension IDs"""
    try:
        print("🔌 Connecting to Railway database...")
        # Validate environment configuration
        validate_config()
        
        # Get Railway database configuration from environment variables
        railway_config = get_railway_db_config()
        
        conn = psycopg2.connect(**railway_config)(**get_railway_db_config())
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Get existing call queues, users, and pbx extensions
        cursor.execute("SELECT id FROM call_queues")
        queue_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE organization_id = 1")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM pbx_extensions WHERE organization_id = 1")
        extension_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(queue_ids)} queues, {len(user_ids)} users, {len(extension_ids)} extensions")
        
        if queue_ids and user_ids and extension_ids:
            # Clear existing queue members
            cursor.execute("DELETE FROM call_queue_members")
            print("🧹 Cleared existing queue members")
            
            # Create queue members with valid extension IDs
            member_count = 0
            for queue_id in queue_ids:
                # Assign 2-4 users to each queue
                queue_users = random.sample(user_ids, min(len(user_ids), random.randint(2, 4)))
                
                for i, user_id in enumerate(queue_users):
                    # Use a valid extension ID
                    extension_id = extension_ids[i % len(extension_ids)]
                    
                    cursor.execute("""
                        INSERT INTO call_queue_members (
                            queue_id, user_id, extension_id, penalty,
                            paused, status, last_call_time, total_calls,
                            answered_calls, talk_time, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        queue_id,
                        user_id,
                        extension_id,  # Use valid extension ID
                        random.randint(1, 10),     # penalty
                        False,                     # not paused
                        'logged_in',               # status
                        datetime.now() - timedelta(minutes=random.randint(5, 120)),  # last_call_time
                        random.randint(10, 100),   # total calls
                        random.randint(8, 95),     # answered calls
                        random.randint(120, 600),  # talk time in seconds
                        datetime.now(),
                        datetime.now()
                    ))
                    member_count += 1
            
            print(f"  ✓ Created {member_count} call queue members with valid extension IDs")
        else:
            print("  ❌ Missing required data:")
            print(f"    - Queues: {len(queue_ids) if queue_ids else 0}")
            print(f"    - Users: {len(user_ids) if user_ids else 0}")
            print(f"    - Extensions: {len(extension_ids) if extension_ids else 0}")
        
        print("\n" + "=" * 60)
        print("🎉 Call queue members fixed successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing call queue members: {e}")
        return False

if __name__ == "__main__":
    fix_call_queue_members()
