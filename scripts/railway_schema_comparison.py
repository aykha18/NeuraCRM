#!/usr/bin/env python3
"""
Railway Database Schema Comparison Script
========================================

This script compares the local database schema with Railway database schema
and generates SQL commands to deploy the telephony module changes.

Usage:
    python scripts/railway_schema_comparison.py

Requirements:
    - Local PostgreSQL database running
    - Railway database connection details
    - psycopg2 installed
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
import json
from datetime import datetime
from typing import Dict, List, Set, Tuple

# Database configurations
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'aykha123',
    'port': 5432
}

# Railway DB config now loaded from environment variables

class DatabaseSchemaComparator:
    def __init__(self):
        self.local_conn = None
        self.railway_conn = None
        self.local_tables = {}
        self.railway_tables = {}
        self.missing_tables = []
        self.missing_columns = {}
        self.missing_indexes = {}
        self.missing_constraints = {}
        
    def connect_databases(self):
        """Connect to both local and Railway databases"""
        try:
            print("🔌 Connecting to local database...")
            self.local_conn = psycopg2.connect(**LOCAL_DB_CONFIG)
            self.local_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print("✅ Local database connected successfully")
            
            print("🔌 Connecting to Railway database...")
            self.railway_conn = psycopg2.connect(**get_railway_db_config())
            self.railway_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print("✅ Railway database connected successfully")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def get_table_schema(self, connection, db_name: str) -> Dict:
        """Get complete table schema from database"""
        cursor = connection.cursor()
        schema = {}
        
        try:
            # Get all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"📋 Found {len(tables)} tables in {db_name}")
            
            for table_name in tables:
                # Get columns
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default,
                           character_maximum_length, numeric_precision, numeric_scale
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                columns = {}
                for row in cursor.fetchall():
                    columns[row[0]] = {
                        'data_type': row[1],
                        'is_nullable': row[2],
                        'column_default': row[3],
                        'character_maximum_length': row[4],
                        'numeric_precision': row[5],
                        'numeric_scale': row[6]
                    }
                
                # Get indexes
                cursor.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename = %s;
                """, (table_name,))
                
                indexes = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Get foreign key constraints
                cursor.execute("""
                    SELECT conname, contype, pg_get_constraintdef(oid)
                    FROM pg_constraint 
                    WHERE conrelid = (
                        SELECT oid FROM pg_class WHERE relname = %s
                    );
                """, (table_name,))
                
                constraints = {}
                for row in cursor.fetchall():
                    constraints[row[0]] = {
                        'type': row[1],
                        'definition': row[2]
                    }
                
                schema[table_name] = {
                    'columns': columns,
                    'indexes': indexes,
                    'constraints': constraints
                }
                
        except Exception as e:
            print(f"❌ Error getting schema from {db_name}: {e}")
            
        return schema
    
    def compare_schemas(self):
        """Compare local and Railway schemas"""
        print("\n🔍 Comparing database schemas...")
        
        # Get schemas from both databases
        self.local_tables = self.get_table_schema(self.local_conn, "Local")
        self.railway_tables = self.get_table_schema(self.railway_conn, "Railway")
        
        local_table_names = set(self.local_tables.keys())
        railway_table_names = set(self.railway_tables.keys())
        
        # Find missing tables
        self.missing_tables = list(local_table_names - railway_table_names)
        
        # Find tables that exist in both but have different columns
        common_tables = local_table_names & railway_table_names
        
        for table_name in common_tables:
            local_columns = set(self.local_tables[table_name]['columns'].keys())
            railway_columns = set(self.railway_tables[table_name]['columns'].keys())
            
            missing_columns = local_columns - railway_columns
            if missing_columns:
                self.missing_columns[table_name] = missing_columns
        
        # Find missing indexes and constraints
        for table_name in common_tables:
            local_indexes = set(self.local_tables[table_name]['indexes'].keys())
            railway_indexes = set(self.railway_tables[table_name]['indexes'].keys())
            
            missing_indexes = local_indexes - railway_indexes
            if missing_indexes:
                self.missing_indexes[table_name] = missing_indexes
            
            local_constraints = set(self.local_tables[table_name]['constraints'].keys())
            railway_constraints = set(self.railway_tables[table_name]['constraints'].keys())
            
            missing_constraints = local_constraints - railway_constraints
            if missing_constraints:
                self.missing_constraints[table_name] = missing_constraints
    
    def generate_telephony_tables_sql(self) -> str:
        """Generate SQL for creating telephony tables"""
        sql_statements = []
        
        # Telephony table definitions
        telephony_tables = {
            'pbx_providers': """
                CREATE TABLE IF NOT EXISTS pbx_providers (
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
            """,
            
            'pbx_extensions': """
                CREATE TABLE IF NOT EXISTS pbx_extensions (
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
            """,
            
            'calls': """
                CREATE TABLE IF NOT EXISTS calls (
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
            """,
            
            'call_activities': """
                CREATE TABLE IF NOT EXISTS call_activities (
                    id SERIAL PRIMARY KEY,
                    call_id INTEGER NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('answer', 'hold', 'unhold', 'transfer', 'conference', 'mute', 'unmute', 'hangup')),
                    activity_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'call_queues': """
                CREATE TABLE IF NOT EXISTS call_queues (
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
            """,
            
            'call_queue_members': """
                CREATE TABLE IF NOT EXISTS call_queue_members (
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
            """,
            
            'call_campaigns': """
                CREATE TABLE IF NOT EXISTS call_campaigns (
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
            """,
            
            'campaign_calls': """
                CREATE TABLE IF NOT EXISTS campaign_calls (
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
            """,
            
            'call_analytics': """
                CREATE TABLE IF NOT EXISTS call_analytics (
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
            """
        }
        
        sql_statements.append("-- ========================================")
        sql_statements.append("-- TELEPHONY MODULE TABLES CREATION")
        sql_statements.append("-- ========================================")
        sql_statements.append("")
        
        for table_name, table_sql in telephony_tables.items():
            if table_name in self.missing_tables:
                sql_statements.append(f"-- Creating table: {table_name}")
                sql_statements.append(table_sql.strip())
                sql_statements.append("")
        
        # Add indexes
        sql_statements.append("-- ========================================")
        sql_statements.append("-- TELEPHONY MODULE INDEXES")
        sql_statements.append("-- ========================================")
        sql_statements.append("")
        
        indexes = [
            ("calls", "idx_calls_organization_id", "CREATE INDEX IF NOT EXISTS idx_calls_organization_id ON calls(organization_id);"),
            ("calls", "idx_calls_start_time", "CREATE INDEX IF NOT EXISTS idx_calls_start_time ON calls(start_time);"),
            ("calls", "idx_calls_status", "CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);"),
            ("calls", "idx_calls_direction", "CREATE INDEX IF NOT EXISTS idx_calls_direction ON calls(direction);"),
            ("calls", "idx_calls_agent_id", "CREATE INDEX IF NOT EXISTS idx_calls_agent_id ON calls(agent_id);"),
            ("calls", "idx_calls_queue_id", "CREATE INDEX IF NOT EXISTS idx_calls_queue_id ON calls(queue_id);"),
            ("call_activities", "idx_call_activities_call_id", "CREATE INDEX IF NOT EXISTS idx_call_activities_call_id ON call_activities(call_id);"),
            ("call_activities", "idx_call_activities_timestamp", "CREATE INDEX IF NOT EXISTS idx_call_activities_timestamp ON call_activities(timestamp);"),
            ("call_queue_members", "idx_call_queue_members_queue_id", "CREATE INDEX IF NOT EXISTS idx_call_queue_members_queue_id ON call_queue_members(queue_id);"),
            ("call_queue_members", "idx_call_queue_members_user_id", "CREATE INDEX IF NOT EXISTS idx_call_queue_members_user_id ON call_queue_members(user_id);"),
            ("campaign_calls", "idx_campaign_calls_campaign_id", "CREATE INDEX IF NOT EXISTS idx_campaign_calls_campaign_id ON campaign_calls(campaign_id);"),
            ("call_analytics", "idx_call_analytics_date", "CREATE INDEX IF NOT EXISTS idx_call_analytics_date ON call_analytics(date);"),
            ("call_analytics", "idx_call_analytics_org_date", "CREATE INDEX IF NOT EXISTS idx_call_analytics_org_date ON call_analytics(organization_id, date);")
        ]
        
        for table_name, index_name, index_sql in indexes:
            if table_name in self.missing_tables:
                sql_statements.append(f"-- Creating index: {index_name}")
                sql_statements.append(index_sql)
                sql_statements.append("")
        
        return "\n".join(sql_statements)
    
    def generate_migration_sql(self) -> str:
        """Generate complete migration SQL"""
        sql_statements = []
        
        # Header
        sql_statements.append("-- ========================================")
        sql_statements.append(f"-- RAILWAY DATABASE MIGRATION")
        sql_statements.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sql_statements.append("-- Purpose: Deploy telephony module to Railway")
        sql_statements.append("-- ========================================")
        sql_statements.append("")
        
        # Add telephony tables
        telephony_sql = self.generate_telephony_tables_sql()
        sql_statements.append(telephony_sql)
        
        # Summary
        sql_statements.append("-- ========================================")
        sql_statements.append("-- MIGRATION SUMMARY")
        sql_statements.append("-- ========================================")
        sql_statements.append(f"-- Tables to be created: {len(self.missing_tables)}")
        if self.missing_tables:
            sql_statements.append(f"-- Missing tables: {', '.join(self.missing_tables)}")
        
        return "\n".join(sql_statements)
    
    def save_migration_file(self, sql_content: str):
        """Save migration SQL to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"railway_telephony_migration_{timestamp}.sql"
        filepath = os.path.join("scripts", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        print(f"💾 Migration SQL saved to: {filepath}")
        return filepath
    
    def print_comparison_report(self):
        """Print detailed comparison report"""
        print("\n" + "="*60)
        print("📊 DATABASE SCHEMA COMPARISON REPORT")
        print("="*60)
        
        print(f"\n📋 Local Database Tables: {len(self.local_tables)}")
        print(f"📋 Railway Database Tables: {len(self.railway_tables)}")
        
        if self.missing_tables:
            print(f"\n❌ Missing Tables in Railway ({len(self.missing_tables)}):")
            for table in self.missing_tables:
                print(f"   - {table}")
        else:
            print("\n✅ All tables exist in Railway")
        
        if self.missing_columns:
            print(f"\n❌ Missing Columns ({len(self.missing_columns)} tables):")
            for table, columns in self.missing_columns.items():
                print(f"   - {table}: {', '.join(columns)}")
        else:
            print("\n✅ All columns match between databases")
        
        if self.missing_indexes:
            print(f"\n❌ Missing Indexes ({len(self.missing_indexes)} tables):")
            for table, indexes in self.missing_indexes.items():
                print(f"   - {table}: {', '.join(indexes)}")
        
        if self.missing_constraints:
            print(f"\n❌ Missing Constraints ({len(self.missing_constraints)} tables):")
            for table, constraints in self.missing_constraints.items():
                print(f"   - {table}: {', '.join(constraints)}")
        
        print("\n" + "="*60)
    
    def close_connections(self):
        """Close database connections"""
        if self.local_conn:
            self.local_conn.close()
        if self.railway_conn:
            self.railway_conn.close()
        print("🔌 Database connections closed")

def main():
    print("🚀 Railway Database Schema Comparison Tool")
    print("=" * 50)
    
    comparator = DatabaseSchemaComparator()
    
    try:
        # Connect to databases
        comparator.connect_databases()
        
        # Compare schemas
        comparator.compare_schemas()
        
        # Print report
        comparator.print_comparison_report()
        
        # Generate migration SQL
        migration_sql = comparator.generate_migration_sql()
        
        # Save to file
        migration_file = comparator.save_migration_file(migration_sql)
        
        print(f"\n✅ Migration ready!")
        print(f"📄 SQL file: {migration_file}")
        print(f"\n🔧 To deploy to Railway:")
        print(f"   1. Review the SQL file: {migration_file}")
        print(f"   2. Connect to Railway database")
        print(f"   3. Execute the SQL commands")
        
        # Ask if user wants to execute migration
        print(f"\n❓ Would you like to execute the migration now? (y/n): ", end="")
        response = input().lower().strip()
        
        if response == 'y':
            print("\n🚀 Executing migration on Railway database...")
            cursor = comparator.railway_conn.cursor()
            
            # Execute each statement separately
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            
            for i, statement in enumerate(statements):
                if statement:
                    try:
                        cursor.execute(statement)
                        print(f"✅ Executed statement {i+1}/{len(statements)}")
                    except Exception as e:
                        print(f"❌ Error executing statement {i+1}: {e}")
                        print(f"Statement: {statement[:100]}...")
            
            comparator.railway_conn.commit()
            print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        comparator.close_connections()

if __name__ == "__main__":
    main()
