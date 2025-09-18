#!/usr/bin/env python3
"""
Check Knowledge Base tables and columns in Railway database
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Railway database URL
RAILWAY_DB_URL = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"

def check_knowledge_base_tables():
    """Check Knowledge Base tables and columns in Railway"""
    try:
        # Create engine
        engine = create_engine(RAILWAY_DB_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connected to Railway database!")
        
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        # Check for Knowledge Base related tables
        kb_tables = [table for table in all_tables if 'knowledge' in table.lower() or 'kb' in table.lower()]
        
        print(f"\n📋 All Knowledge Base related tables:")
        for table in kb_tables:
            print(f"  ✅ {table}")
        
        # Check knowledge_base_articles table specifically
        if 'knowledge_base_articles' in all_tables:
            print(f"\n🔍 Checking knowledge_base_articles table:")
            columns = inspector.get_columns('knowledge_base_articles')
            print(f"  📊 Total columns: {len(columns)}")
            
            # Check for specific important columns
            column_names = [col['name'] for col in columns]
            required_columns = [
                'id', 'title', 'content', 'summary', 'category', 
                'status', 'author_id', 'organization_id', 'created_at'
            ]
            
            print(f"  📋 All columns: {column_names}")
            
            missing_columns = [col for col in required_columns if col not in column_names]
            if missing_columns:
                print(f"  ⚠️  Missing required columns: {missing_columns}")
            else:
                print(f"  ✅ All required columns present")
                
            # Show sample data
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM knowledge_base_articles"))
                count = result.fetchone()[0]
                print(f"  📈 Total articles: {count}")
                
                if count > 0:
                    result = conn.execute(text("SELECT id, title, status, created_at FROM knowledge_base_articles LIMIT 5"))
                    articles = result.fetchall()
                    print(f"  📝 Sample articles:")
                    for article in articles:
                        print(f"    - ID: {article[0]}, Title: {article[1]}, Status: {article[2]}, Created: {article[3]}")
        else:
            print(f"\n❌ knowledge_base_articles table does NOT exist!")
            
        # Check support_tickets table
        if 'support_tickets' in all_tables:
            print(f"\n🔍 Checking support_tickets table:")
            columns = inspector.get_columns('support_tickets')
            print(f"  📊 Total columns: {len(columns)}")
            
            # Check for recently added columns
            column_names = [col['name'] for col in columns]
            new_columns = ['assignment_reason', 'assignment_type', 'queue_id', 'resolution', 'resolution_notes']
            
            present_new_columns = [col for col in new_columns if col in column_names]
            print(f"  ✅ Recently added columns present: {present_new_columns}")
            
            # Show sample data
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM support_tickets"))
                count = result.fetchone()[0]
                print(f"  📈 Total tickets: {count}")
                
                if count > 0:
                    result = conn.execute(text("SELECT id, ticket_number, title, status, created_at FROM support_tickets LIMIT 5"))
                    tickets = result.fetchall()
                    print(f"  🎫 Sample tickets:")
                    for ticket in tickets:
                        print(f"    - ID: {ticket[0]}, Number: {ticket[1]}, Title: {ticket[2]}, Status: {ticket[3]}, Created: {ticket[4]}")
        
        print(f"\n🎉 Knowledge Base tables check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking Knowledge Base tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_knowledge_base_tables()
    sys.exit(0 if success else 1)
