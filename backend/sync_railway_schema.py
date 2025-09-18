#!/usr/bin/env python3
"""
Sync Railway database schema with local models
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Railway database URL
RAILWAY_DB_URL = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"

def get_existing_tables(engine):
    """Get list of existing tables in the database"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def sync_knowledge_base_schema():
    """Sync knowledge base schema with Railway database"""
    try:
        # Create engine
        engine = create_engine(RAILWAY_DB_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connected to Railway database!")
        
        # Get existing tables
        existing_tables = get_existing_tables(engine)
        print(f"📋 Existing tables: {existing_tables}")
        
        # Check if knowledge_base_articles exists
        if 'knowledge_base_articles' not in existing_tables:
            print("🔧 Creating knowledge_base_articles table...")
            create_kb_table_sql = """
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
            with engine.connect() as conn:
                conn.execute(text(create_kb_table_sql))
                conn.commit()
                print("✅ Created knowledge_base_articles table!")
        else:
            print("ℹ️  knowledge_base_articles table already exists")
        
        # Check if support_tickets exists
        if 'support_tickets' not in existing_tables:
            print("🔧 Creating support_tickets table...")
            create_tickets_table_sql = """
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
            with engine.connect() as conn:
                conn.execute(text(create_tickets_table_sql))
                conn.commit()
                print("✅ Created support_tickets table!")
        else:
            print("ℹ️  support_tickets table already exists")
        
        # Check if support_comments exists
        if 'support_comments' not in existing_tables:
            print("🔧 Creating support_comments table...")
            create_comments_table_sql = """
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
            with engine.connect() as conn:
                conn.execute(text(create_comments_table_sql))
                conn.commit()
                print("✅ Created support_comments table!")
        else:
            print("ℹ️  support_comments table already exists")
        
        # Check if support_agents exists
        if 'support_agents' not in existing_tables:
            print("🔧 Creating support_agents table...")
            create_agents_table_sql = """
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
            with engine.connect() as conn:
                conn.execute(text(create_agents_table_sql))
                conn.commit()
                print("✅ Created support_agents table!")
        else:
            print("ℹ️  support_agents table already exists")
        
        # Check if customer_satisfaction_surveys exists
        if 'customer_satisfaction_surveys' not in existing_tables:
            print("🔧 Creating customer_satisfaction_surveys table...")
            create_surveys_table_sql = """
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
            with engine.connect() as conn:
                conn.execute(text(create_surveys_table_sql))
                conn.commit()
                print("✅ Created customer_satisfaction_surveys table!")
        else:
            print("ℹ️  customer_satisfaction_surveys table already exists")
        
        # Check if support_slas exists
        if 'support_slas' not in existing_tables:
            print("🔧 Creating support_slas table...")
            create_slas_table_sql = """
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
            with engine.connect() as conn:
                conn.execute(text(create_slas_table_sql))
                conn.commit()
                print("✅ Created support_slas table!")
        else:
            print("ℹ️  support_slas table already exists")
        
        print("🎉 Database schema sync completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing database schema: {e}")
        return False

if __name__ == "__main__":
    success = sync_knowledge_base_schema()
    sys.exit(0 if success else 1)
