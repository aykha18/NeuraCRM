#!/usr/bin/env python3
"""
Apply database changes to Railway PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set the database URL
DATABASE_URL = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"

def create_knowledge_base_table():
    """Create the knowledge_base_articles table"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create knowledge_base_articles table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS knowledge_base_articles (
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
            published_at TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (author_id) REFERENCES users(id),
            FOREIGN KEY (reviewer_id) REFERENCES users(id)
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Created knowledge_base_articles table!")
        
        # Create support_tickets table if it doesn't exist
        create_support_tickets_sql = """
        CREATE TABLE IF NOT EXISTS support_tickets (
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
            closed_at TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (assigned_to_id) REFERENCES users(id)
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_support_tickets_sql))
            conn.commit()
            print("✅ Created support_tickets table!")
        
        # Create support_comments table if it doesn't exist
        create_support_comments_sql = """
        CREATE TABLE IF NOT EXISTS support_comments (
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_internal BOOLEAN DEFAULT FALSE,
            comment_type VARCHAR DEFAULT 'comment',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES support_tickets(id),
            FOREIGN KEY (author_id) REFERENCES users(id)
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_support_comments_sql))
            conn.commit()
            print("✅ Created support_comments table!")
        
        print("🎉 All database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    success = create_knowledge_base_table()
    sys.exit(0 if success else 1)
