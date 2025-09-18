#!/usr/bin/env python3
"""
Compare local database schema with Railway database schema
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Railway database URL
RAILWAY_DB_URL = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"

def get_table_columns(engine, table_name):
    """Get column information for a specific table"""
    inspector = inspect(engine)
    if table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        return {col['name']: col for col in columns}
    return {}

def compare_schemas():
    """Compare local and Railway database schemas"""
    try:
        # Create Railway engine
        railway_engine = create_engine(RAILWAY_DB_URL)
        
        # Test Railway connection
        with railway_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connected to Railway database!")
        
        # Get Railway tables
        railway_inspector = inspect(railway_engine)
        railway_tables = railway_inspector.get_table_names()
        print(f"📋 Railway tables: {railway_tables}")
        
        # Check specific tables we need
        tables_to_check = [
            'knowledge_base_articles',
            'support_tickets', 
            'support_comments',
            'support_agents',
            'customer_satisfaction_surveys',
            'support_slas'
        ]
        
        for table_name in tables_to_check:
            print(f"\n🔍 Checking table: {table_name}")
            
            if table_name in railway_tables:
                print(f"  ✅ Table exists in Railway")
                columns = get_table_columns(railway_engine, table_name)
                print(f"  📊 Columns ({len(columns)}): {list(columns.keys())}")
                
                # Check for specific important columns
                if table_name == 'knowledge_base_articles':
                    required_columns = ['id', 'title', 'content', 'category', 'status', 'author_id']
                    missing_columns = [col for col in required_columns if col not in columns]
                    if missing_columns:
                        print(f"  ⚠️  Missing columns: {missing_columns}")
                    else:
                        print(f"  ✅ All required columns present")
                        
                elif table_name == 'support_tickets':
                    required_columns = ['id', 'ticket_number', 'title', 'description', 'priority', 'status', 'customer_name']
                    missing_columns = [col for col in required_columns if col not in columns]
                    if missing_columns:
                        print(f"  ⚠️  Missing columns: {missing_columns}")
                    else:
                        print(f"  ✅ All required columns present")
            else:
                print(f"  ❌ Table does NOT exist in Railway")
                
                # Create the table
                print(f"  🔧 Creating {table_name} table...")
                create_table_sql = get_create_table_sql(table_name)
                
                with railway_engine.connect() as conn:
                    conn.execute(text(create_table_sql))
                    conn.commit()
                    print(f"  ✅ Created {table_name} table!")
        
        print(f"\n🎉 Schema comparison and sync completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error comparing schemas: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_create_table_sql(table_name):
    """Get CREATE TABLE SQL for specific tables"""
    
    if table_name == 'knowledge_base_articles':
        return """
        CREATE TABLE knowledge_base_articles (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            slug VARCHAR UNIQUE NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            category VARCHAR NOT NULL,
            subcategory VARCHAR,
            tags JSON,
            status VARCHAR DEFAULT 'draft',
            visibility VARCHAR DEFAULT 'public',
            featured BOOLEAN DEFAULT FALSE,
            meta_description VARCHAR,
            view_count INTEGER DEFAULT 0,
            helpful_count INTEGER DEFAULT 0,
            not_helpful_count INTEGER DEFAULT 0,
            author_id INTEGER NOT NULL,
            reviewer_id INTEGER,
            approved_at TIMESTAMP,
            last_reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP
        );
        """
        
    elif table_name == 'support_tickets':
        return """
        CREATE TABLE support_tickets (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL,
            ticket_number VARCHAR UNIQUE NOT NULL,
            title VARCHAR NOT NULL,
            description TEXT NOT NULL,
            priority VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            subcategory VARCHAR,
            customer_name VARCHAR NOT NULL,
            customer_email VARCHAR NOT NULL,
            assigned_to_id INTEGER,
            sla_deadline TIMESTAMP,
            first_response_at TIMESTAMP,
            resolution_deadline TIMESTAMP,
            escalated BOOLEAN DEFAULT FALSE,
            escalated_at TIMESTAMP,
            satisfaction_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            closed_at TIMESTAMP
        );
        """
        
    elif table_name == 'support_comments':
        return """
        CREATE TABLE support_comments (
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_internal BOOLEAN DEFAULT FALSE,
            comment_type VARCHAR DEFAULT 'comment',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
    elif table_name == 'support_agents':
        return """
        CREATE TABLE support_agents (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR NOT NULL,
            skills JSON,
            workload INTEGER DEFAULT 0,
            max_tickets INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
    elif table_name == 'customer_satisfaction_surveys':
        return """
        CREATE TABLE customer_satisfaction_surveys (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL,
            ticket_id INTEGER,
            customer_email VARCHAR NOT NULL,
            overall_satisfaction INTEGER,
            response_time_rating INTEGER,
            resolution_quality_rating INTEGER,
            agent_helpfulness_rating INTEGER,
            nps_score INTEGER,
            feedback TEXT,
            survey_sent_at TIMESTAMP,
            survey_completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
    elif table_name == 'support_slas':
        return """
        CREATE TABLE support_slas (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            description TEXT,
            priority VARCHAR NOT NULL,
            first_response_time_hours INTEGER NOT NULL,
            resolution_time_hours INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    return ""

if __name__ == "__main__":
    success = compare_schemas()
    sys.exit(0 if success else 1)
