#!/usr/bin/env python3
"""
Deploy Telephony Module to Railway Database
==========================================

This script deploys the telephony module schema to Railway PostgreSQL database.

Usage:
    python scripts/deploy_telephony_to_railway.py
"""

import os
import sys
import psycopg2

import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Railway Database Configuration
# Railway DB config now loaded from environment variables

def deploy_telephony_to_railway():
    """Deploy telephony schema to Railway database"""
    print("🚀 Deploying Telephony Module to Railway Database")
    print("=" * 50)
    
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
        
        # Check existing telephony tables
        print("\n🔍 Checking existing telephony tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%call%' OR table_name LIKE '%pbx%')
            ORDER BY table_name
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Found {len(existing_tables)} existing telephony tables:")
        for table in existing_tables:
            print(f"   - {table}")
        
        # Drop existing telephony tables if they exist (to recreate with correct schema)
        print("\n🗑️  Dropping existing telephony tables...")
        telephony_tables = [
            'call_analytics',
            'campaign_calls', 
            'call_campaigns',
            'call_queue_members',
            'call_queues',
            'call_activities',
            'calls',
            'pbx_extensions',
            'pbx_providers'
        ]
        
        for table in telephony_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                print(f"   ✅ Dropped {table}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {table}: {e}")
        
        # Create telephony tables with correct schema
        print("\n🏗️  Creating telephony tables with correct schema...")
        
        # PBX Providers
        cursor.execute("""
            CREATE TABLE pbx_providers (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                created_by INTEGER NOT NULL REFERENCES users(id),
                name VARCHAR(255) NOT NULL,
                provider_type VARCHAR(50) NOT NULL CHECK (provider_type IN ('asterisk', 'freepbx', '3cx', 'twilio', 'custom')),
                display_name VARCHAR(255),
                description TEXT,
                host VARCHAR(255),
                port INTEGER DEFAULT 8088,
                username VARCHAR(255),
                password TEXT,
                api_key TEXT,
                context VARCHAR(100) DEFAULT 'default',
                caller_id_field VARCHAR(100) DEFAULT 'CallerIDNum',
                dialplan_context VARCHAR(100) DEFAULT 'from-internal',
                recording_enabled BOOLEAN DEFAULT TRUE,
                recording_path VARCHAR(500) DEFAULT '/var/spool/asterisk/monitor',
                transcription_enabled BOOLEAN DEFAULT FALSE,
                cdr_enabled BOOLEAN DEFAULT TRUE,
                cdr_path VARCHAR(500) DEFAULT '/var/log/asterisk/cdr-csv',
                webhook_url VARCHAR(500),
                webhook_secret VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                is_primary BOOLEAN DEFAULT FALSE,
                auto_assign_calls BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync TIMESTAMP
            );
        """)
        print("   ✅ Created pbx_providers")
        
        # PBX Extensions
        cursor.execute("""
            CREATE TABLE pbx_extensions (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                provider_id INTEGER NOT NULL REFERENCES pbx_providers(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                extension_number VARCHAR(20) NOT NULL,
                extension_type VARCHAR(50) DEFAULT 'sip' CHECK (extension_type IN ('sip', 'iax2', 'pjsip', 'dahdi')),
                secret VARCHAR(255),
                callerid VARCHAR(255),
                context VARCHAR(100) DEFAULT 'default',
                host VARCHAR(50) DEFAULT 'dynamic',
                nat VARCHAR(20) DEFAULT 'force_rport,comedia',
                canreinvite VARCHAR(20) DEFAULT 'no',
                dtmfmode VARCHAR(20) DEFAULT 'rfc2833',
                disallow VARCHAR(100) DEFAULT 'all',
                allow VARCHAR(100) DEFAULT 'ulaw,alaw,gsm',
                qualify VARCHAR(10) DEFAULT 'yes',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created pbx_extensions")
        
        # Call Queues
        cursor.execute("""
            CREATE TABLE call_queues (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                provider_id INTEGER NOT NULL REFERENCES pbx_providers(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                queue_number VARCHAR(50) NOT NULL,
                strategy VARCHAR(50) DEFAULT 'ringall' CHECK (strategy IN ('ringall', 'leastrecent', 'fewestcalls', 'random', 'rrmemory', 'linear', 'wrandom', 'rrordered')),
                timeout INTEGER DEFAULT 30,
                retry INTEGER DEFAULT 5,
                wrapup_time INTEGER DEFAULT 30,
                max_wait_time INTEGER DEFAULT 300,
                music_on_hold VARCHAR(100) DEFAULT 'default',
                announce_frequency INTEGER DEFAULT 30,
                announce_position BOOLEAN DEFAULT TRUE,
                announce_hold_time BOOLEAN DEFAULT TRUE,
                max_calls_per_agent INTEGER DEFAULT 1,
                join_empty BOOLEAN DEFAULT TRUE,
                leave_when_empty BOOLEAN DEFAULT FALSE,
                priority INTEGER DEFAULT 0,
                skill_based_routing BOOLEAN DEFAULT FALSE,
                required_skills TEXT[],
                is_active BOOLEAN DEFAULT TRUE,
                current_calls INTEGER DEFAULT 0,
                current_agents INTEGER DEFAULT 0,
                total_calls INTEGER DEFAULT 0,
                answered_calls INTEGER DEFAULT 0,
                abandoned_calls INTEGER DEFAULT 0,
                avg_wait_time INTEGER DEFAULT 0,
                avg_talk_time INTEGER DEFAULT 0,
                service_level INTEGER DEFAULT 80,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created call_queues")
        
        # Call Queue Members (with correct schema matching the model)
        cursor.execute("""
            CREATE TABLE call_queue_members (
                id SERIAL PRIMARY KEY,
                queue_id INTEGER NOT NULL REFERENCES call_queues(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                extension_id INTEGER REFERENCES pbx_extensions(id) ON DELETE SET NULL,
                penalty INTEGER DEFAULT 0,
                paused BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'logged_out' CHECK (status IN ('logged_in', 'logged_out', 'busy', 'offline')),
                last_call_time TIMESTAMP,
                total_calls INTEGER DEFAULT 0,
                answered_calls INTEGER DEFAULT 0,
                talk_time INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(queue_id, user_id)
            );
        """)
        print("   ✅ Created call_queue_members")
        
        # Calls
        cursor.execute("""
            CREATE TABLE calls (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                provider_id INTEGER REFERENCES pbx_providers(id) ON DELETE SET NULL,
                extension_id INTEGER REFERENCES pbx_extensions(id) ON DELETE SET NULL,
                unique_id VARCHAR(50) UNIQUE,
                pbx_call_id VARCHAR(50),
                session_id VARCHAR(100),
                caller_id VARCHAR(50),
                caller_name VARCHAR(255),
                called_number VARCHAR(50),
                called_name VARCHAR(255),
                direction VARCHAR(20) NOT NULL CHECK (direction IN ('inbound', 'outbound', 'internal')),
                call_type VARCHAR(50) DEFAULT 'voice' CHECK (call_type IN ('voice', 'video', 'conference')),
                status VARCHAR(20) DEFAULT 'ringing' CHECK (status IN ('ringing', 'answered', 'completed', 'busy', 'no_answer', 'failed', 'cancelled')),
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answer_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER DEFAULT 0,
                talk_time INTEGER DEFAULT 0,
                hold_time INTEGER DEFAULT 0,
                wait_time INTEGER DEFAULT 0,
                quality_score DECIMAL(3,2),
                recording_url VARCHAR(500),
                recording_duration INTEGER,
                transcription_url VARCHAR(500),
                transcription_text TEXT,
                disposition VARCHAR(100),
                hangup_cause VARCHAR(50),
                notes TEXT,
                cost DECIMAL(10,4),
                cost_currency VARCHAR(3) DEFAULT 'USD',
                cdr_data JSONB,
                agent_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                queue_id INTEGER REFERENCES call_queues(id) ON DELETE SET NULL,
                contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
                lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
                deal_id INTEGER REFERENCES deals(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created calls")
        
        # Call Activities
        cursor.execute("""
            CREATE TABLE call_activities (
                id SERIAL PRIMARY KEY,
                call_id INTEGER NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('answer', 'hold', 'unhold', 'transfer', 'conference', 'mute', 'unmute', 'hangup')),
                activity_data JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created call_activities")
        
        # Call Campaigns
        cursor.execute("""
            CREATE TABLE call_campaigns (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                created_by INTEGER NOT NULL REFERENCES users(id),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                campaign_type VARCHAR(50) DEFAULT 'outbound' CHECK (campaign_type IN ('outbound', 'survey', 'reminder')),
                status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                daily_start_time TIME DEFAULT '09:00:00',
                daily_end_time TIME DEFAULT '17:00:00',
                max_calls_per_day INTEGER DEFAULT 100,
                max_calls_per_hour INTEGER DEFAULT 10,
                retry_attempts INTEGER DEFAULT 3,
                retry_delay INTEGER DEFAULT 3600,
                script TEXT,
                target_list JSONB,
                filters JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created call_campaigns")
        
        # Campaign Calls
        cursor.execute("""
            CREATE TABLE campaign_calls (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER NOT NULL REFERENCES call_campaigns(id) ON DELETE CASCADE,
                call_id INTEGER REFERENCES calls(id) ON DELETE SET NULL,
                contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
                lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'calling', 'answered', 'no_answer', 'busy', 'failed', 'completed', 'cancelled')),
                attempt_number INTEGER DEFAULT 1,
                scheduled_time TIMESTAMP,
                attempted_time TIMESTAMP,
                result VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Created campaign_calls")
        
        # Call Analytics
        cursor.execute("""
            CREATE TABLE call_analytics (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                hour INTEGER CHECK (hour >= 0 AND hour <= 23),
                provider_id INTEGER REFERENCES pbx_providers(id) ON DELETE SET NULL,
                queue_id INTEGER REFERENCES call_queues(id) ON DELETE SET NULL,
                agent_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                total_calls INTEGER DEFAULT 0,
                answered_calls INTEGER DEFAULT 0,
                abandoned_calls INTEGER DEFAULT 0,
                avg_wait_time INTEGER DEFAULT 0,
                avg_talk_time INTEGER DEFAULT 0,
                avg_hold_time INTEGER DEFAULT 0,
                service_level DECIMAL(5,2) DEFAULT 0.00,
                first_call_resolution DECIMAL(5,2) DEFAULT 0.00,
                customer_satisfaction DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, date, hour, provider_id, queue_id, agent_id)
            );
        """)
        print("   ✅ Created call_analytics")
        
        # Create indexes
        print("\n📊 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_calls_organization_id ON calls(organization_id);",
            "CREATE INDEX IF NOT EXISTS idx_calls_start_time ON calls(start_time);",
            "CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);",
            "CREATE INDEX IF NOT EXISTS idx_calls_direction ON calls(direction);",
            "CREATE INDEX IF NOT EXISTS idx_calls_agent_id ON calls(agent_id);",
            "CREATE INDEX IF NOT EXISTS idx_calls_queue_id ON calls(queue_id);",
            "CREATE INDEX IF NOT EXISTS idx_call_activities_call_id ON call_activities(call_id);",
            "CREATE INDEX IF NOT EXISTS idx_call_activities_timestamp ON call_activities(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_call_queue_members_queue_id ON call_queue_members(queue_id);",
            "CREATE INDEX IF NOT EXISTS idx_call_queue_members_user_id ON call_queue_members(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_campaign_calls_campaign_id ON campaign_calls(campaign_id);",
            "CREATE INDEX IF NOT EXISTS idx_call_analytics_date ON call_analytics(date);",
            "CREATE INDEX IF NOT EXISTS idx_call_analytics_org_date ON call_analytics(organization_id, date);"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"   ✅ Created index")
            except Exception as e:
                print(f"   ⚠️  Could not create index: {e}")
        
        # Verify deployment
        print("\n🔍 Verifying deployment...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%call%' OR table_name LIKE '%pbx%')
            ORDER BY table_name
        """)
        deployed_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Deployed {len(deployed_tables)} telephony tables:")
        for table in deployed_tables:
            print(f"   ✅ {table}")
        
        conn.close()
        print("\n🎉 Telephony module deployed to Railway successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error deploying to Railway: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Railway Telephony Deployment Tool")
    print("=" * 40)
    
    success = deploy_telephony_to_railway()
    
    if success:
        print("\n✅ Railway deployment completed successfully!")
        print("The telephony module is now available on Railway.")
    else:
        print("\n❌ Railway deployment failed!")
        sys.exit(1)
