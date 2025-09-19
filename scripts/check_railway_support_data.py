#!/usr/bin/env python3
"""
Check Railway Support Data
=========================

This script checks the support data in Railway and identifies the issue.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def check_railway_support_data():
    """Check Railway support data and organization mapping"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Check users and their organizations
        print("\n👥 USERS AND ORGANIZATIONS:")
        cursor.execute("SELECT id, name, email, organization_id FROM users ORDER BY id")
        users = cursor.fetchall()
        
        for user in users:
            print(f"  User {user[0]}: {user[1]} ({user[2]}) -> Org {user[3]}")
        
        # Check support tickets by organization
        print("\n🎫 SUPPORT TICKETS BY ORGANIZATION:")
        cursor.execute("""
            SELECT organization_id, COUNT(*) as ticket_count 
            FROM support_tickets 
            GROUP BY organization_id 
            ORDER BY organization_id
        """)
        ticket_counts = cursor.fetchall()
        
        for org_id, count in ticket_counts:
            print(f"  Organization {org_id}: {count} tickets")
        
        # Check knowledge base articles by organization
        print("\n📚 KNOWLEDGE BASE ARTICLES BY ORGANIZATION:")
        cursor.execute("""
            SELECT organization_id, COUNT(*) as article_count 
            FROM knowledge_base_articles 
            GROUP BY organization_id 
            ORDER BY organization_id
        """)
        article_counts = cursor.fetchall()
        
        for org_id, count in article_counts:
            print(f"  Organization {org_id}: {count} articles")
        
        # Check if nodeit@node.com user exists and what org they belong to
        print("\n🔍 CHECKING NODEIT USER:")
        cursor.execute("SELECT id, name, email, organization_id FROM users WHERE email = 'nodeit@node.com'")
        nodeit_user = cursor.fetchone()
        
        if nodeit_user:
            print(f"  Found: User {nodeit_user[0]} ({nodeit_user[1]}) -> Org {nodeit_user[3]}")
            
            # Check tickets for this user's organization
            cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE organization_id = %s", (nodeit_user[3],))
            user_tickets = cursor.fetchone()[0]
            print(f"  Tickets for org {nodeit_user[3]}: {user_tickets}")
            
            # Check knowledge base for this user's organization
            cursor.execute("SELECT COUNT(*) FROM knowledge_base_articles WHERE organization_id = %s", (nodeit_user[3],))
            user_articles = cursor.fetchone()[0]
            print(f"  Knowledge base articles for org {nodeit_user[3]}: {user_articles}")
            
            if user_tickets == 0 and user_articles == 0:
                print("\n❌ PROBLEM IDENTIFIED:")
                print(f"  User nodeit@node.com belongs to organization {nodeit_user[3]}")
                print(f"  But all support data is in organization 1")
                print(f"  This is why the frontend shows 'No tickets found'")
                
                print("\n💡 SOLUTION:")
                print("  Need to either:")
                print("  1. Move support data from org 1 to org 18, OR")
                print("  2. Change nodeit user to belong to org 1")
        else:
            print("  ❌ User nodeit@node.com not found in Railway")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking support data: {e}")

if __name__ == "__main__":
    check_railway_support_data()
