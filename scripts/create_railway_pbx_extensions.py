#!/usr/bin/env python3
"""
Create Railway PBX Extensions
============================

Creates PBX extensions for the Call Center module.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import random

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def create_pbx_extensions():
    """Create PBX extensions for Call Center"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Check if extensions already exist
        cursor.execute("SELECT COUNT(*) FROM pbx_extensions WHERE organization_id = 1")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"✓ PBX extensions already exist ({existing_count} extensions)")
            return True
        
        # Get PBX providers and users to associate extensions with
        cursor.execute("SELECT id FROM pbx_providers WHERE organization_id = 1")
        provider_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE organization_id = 1")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not provider_ids:
            print("❌ No PBX providers found")
            return False
        
        if not user_ids:
            print("❌ No users found")
            return False
        
        # Create PBX extensions with valid extension types (sip or pjsip)
        extensions_data = [
            {"extension_number": "101", "extension_type": "sip", "callerid": "Sales Agent"},
            {"extension_number": "102", "extension_type": "sip", "callerid": "Support Agent"},
            {"extension_number": "103", "extension_type": "sip", "callerid": "Technical Agent"},
            {"extension_number": "104", "extension_type": "sip", "callerid": "Billing Agent"},
            {"extension_number": "105", "extension_type": "sip", "callerid": "Manager"},
            {"extension_number": "106", "extension_type": "pjsip", "callerid": "Agent 6"},
            {"extension_number": "107", "extension_type": "pjsip", "callerid": "Agent 7"},
            {"extension_number": "108", "extension_type": "pjsip", "callerid": "Agent 8"},
            {"extension_number": "109", "extension_type": "pjsip", "callerid": "Agent 9"},
            {"extension_number": "110", "extension_type": "sip", "callerid": "Agent 10"}
        ]
        
        created_count = 0
        for i, ext_data in enumerate(extensions_data):
            # Assign users to extensions
            user_id = user_ids[i % len(user_ids)]
            
            cursor.execute("""
                INSERT INTO pbx_extensions (
                    organization_id, provider_id, user_id, extension_number,
                    extension_type, secret, callerid, context, host,
                    nat, canreinvite, dtmfmode, disallow, allow, qualify,
                    is_active, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                1,  # organization_id
                random.choice(provider_ids),  # provider_id
                user_id,  # user_id
                ext_data["extension_number"],
                ext_data["extension_type"],
                f"secret{random.randint(1000, 9999)}",  # secret
                ext_data["callerid"],
                "default",  # context
                "dynamic",  # host
                "yes",  # nat
                "yes",  # canreinvite
                "rfc2833",  # dtmfmode
                "all",  # disallow
                "ulaw,alaw,g729",  # allow
                "yes",  # qualify
                True,  # is_active
                datetime.now(),
                datetime.now()
            ))
            created_count += 1
        
        print(f"✓ Created {created_count} PBX extensions")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating PBX extensions: {e}")
        return False

if __name__ == "__main__":
    create_pbx_extensions()