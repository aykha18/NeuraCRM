#!/usr/bin/env python3
"""
Essential Demo Data Seeder for NeuraCRM
======================================

This script creates essential demo data for The Node Information Technology LLC
to showcase NeuraCRM features with realistic data.

Usage:
    python scripts/seed_essential_demo_data.py

Target: Railway Database - Organization ID 1
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import random
import json
from datetime import datetime, timedelta

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

# Organization ID for The Node IT
ORG_ID = 1

class EssentialDataSeeder:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to Railway database"""
        try:
            print("🔌 Connecting to Railway database...")
            self.conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.conn.cursor()
            print("✅ Connected to Railway database successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Database connection closed")
    
    def seed_organization_and_users(self):
        """Create organization and users"""
        print("\n🏢 Creating Organization and Users...")
        
        # Create organization
        self.cursor.execute("""
            INSERT INTO organizations (id, name, domain, settings, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                domain = EXCLUDED.domain
        """, (
            ORG_ID,
            "The Node Information Technology LLC",
            "nodeit.com",
            json.dumps({
                "industry": "IT Services",
                "size": "50-100 employees",
                "timezone": "Asia/Dubai",
                "currency": "AED"
            }),
            datetime.now() - timedelta(days=365)
        ))
        
        # Create users
        users_data = [
            (1, "Ahmed Al-Rashid", "nodeit@node.com", "admin"),
            (2, "Sarah Johnson", "sarah.johnson@nodeit.com", "manager"),
            (3, "Mohammed Hassan", "mohammed.hassan@nodeit.com", "agent"),
            (4, "Fatima Al-Zahra", "fatima.alzahra@nodeit.com", "agent"),
            (5, "David Chen", "david.chen@nodeit.com", "agent")
        ]
        
        for user_id, name, email, role in users_data:
            self.cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, role, organization_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    role = EXCLUDED.role
            """, (user_id, name, email, "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J1Jpz6VqO", role, ORG_ID, datetime.now() - timedelta(days=300)))
        
        print("✅ Organization and users created")
        return True
    
    def seed_contacts_and_leads(self):
        """Create contacts and leads"""
        print("\n👥 Creating Contacts and Leads...")
        
        companies = [
            "Dubai Municipality", "Emirates NBD", "ADNOC", "Emaar Properties", 
            "Al Futtaim Group", "Dubai Airports", "DEWA", "RTA", "Dubai Police"
        ]
        
        contacts_data = []
        leads_data = []
        
        for i, company in enumerate(companies):
            # Create contacts
            for j in range(2):
                contact_id = i * 2 + j + 1
                contact_data = (
                    f"Contact {contact_id} - {company}",
                    f"contact{contact_id}@{company.lower().replace(' ', '')}.com",
                    f"+971 {random.randint(50, 59)}{random.randint(1000000, 9999999)}",
                    company,
                    random.randint(1, 5),  # owner_id
                    datetime.now() - timedelta(days=random.randint(30, 365)),
                    ORG_ID
                )
                contacts_data.append(contact_data)
                
                # Create leads
                if random.random() < 0.8:  # 80% of contacts become leads
                    services = [
                        "IT Annual Maintenance Contract (AMC)",
                        "Cybersecurity Solutions",
                        "Digital Infrastructure Setup",
                        "ELV Systems Implementation",
                        "Audio-Visual Solutions"
                    ]
                    
                    lead_data = (
                        f"{random.choice(services)} - {company}",
                        contact_id,
                        random.randint(1, 5),  # owner_id
                        random.choice(["new", "contacted", "qualified"]),
                        random.choice(["website", "referral", "cold_call"]),
                        datetime.now() - timedelta(days=random.randint(1, 90)),
                        random.randint(60, 95),  # score
                        datetime.now() - timedelta(hours=random.randint(1, 24)),
                        "High engagement, IT budget available",
                        random.uniform(0.8, 0.95),
                        ORG_ID
                    )
                    leads_data.append(lead_data)
        
        # Insert contacts
        self.cursor.executemany("""
            INSERT INTO contacts (name, email, phone, company, owner_id, created_at, organization_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, contacts_data)
        
        # Insert leads
        self.cursor.executemany("""
            INSERT INTO leads (title, contact_id, owner_id, status, source, created_at, score, score_updated_at, score_factors, score_confidence, organization_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, leads_data)
        
        print("✅ Contacts and leads created")
        return True
    
    def seed_deals_and_stages(self):
        """Create deals and pipeline stages"""
        print("\n💼 Creating Deals and Pipeline...")
        
        # Create stages
        stages_data = [
            ("Qualification", 1, 5),
            ("Proposal", 2, 5),
            ("Negotiation", 3, 5),
            ("Contract Review", 4, 5),
            ("Won", 5, None),
            ("Lost", 0, None)
        ]
        
        for stage_name, stage_order, wip_limit in stages_data:
            self.cursor.execute("""
                INSERT INTO stages (name, "order", wip_limit)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (stage_name, stage_order, wip_limit))
        
        # Get leads and create deals
        self.cursor.execute("SELECT id, title FROM leads WHERE organization_id = %s", (ORG_ID,))
        leads = self.cursor.fetchall()
        
        deals_data = []
        for lead_id, lead_title in leads:
            stage_id = random.choice([1, 2, 3, 4, 5, 6])
            actual_value = random.randint(50000, 500000)
            
            deal_data = (
                lead_title.replace(" - ", " Deal - "),
                actual_value,
                random.randint(1, 5),  # owner_id
                stage_id,
                f"Deal for {lead_title}",
                datetime.now() - timedelta(days=random.randint(1, 180)),
                datetime.now() - timedelta(days=random.randint(1, 30)) if stage_id in [5, 6] else None,
                random.randint(1, 20),  # contact_id
                ORG_ID,
                "active" if stage_id not in [5, 6] else ("won" if stage_id == 5 else "lost")
            )
            deals_data.append(deal_data)
        
        # Insert deals
        self.cursor.executemany("""
            INSERT INTO deals (title, value, owner_id, stage_id, description, created_at, closed_at, contact_id, organization_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, deals_data)
        
        print("✅ Deals and stages created")
        return True
    
    def seed_support_tickets(self):
        """Create support tickets"""
        print("\n🎧 Creating Support Tickets...")
        
        # Create knowledge base articles
        kb_articles = [
            ("IT AMC Support Guide", "Complete guide for IT Annual Maintenance Contract support", "IT Services", "Comprehensive guide covering all aspects of IT AMC support services..."),
            ("Cybersecurity Best Practices", "Essential cybersecurity practices for enterprise clients", "Cybersecurity", "Detailed cybersecurity guidelines including endpoint protection and email security..."),
            ("Digital Infrastructure Setup", "Step-by-step guide for digital infrastructure implementation", "Infrastructure", "Complete guide for setting up servers, storage, and email archival systems...")
        ]
        
        for title, summary, category, content in kb_articles:
            self.cursor.execute("""
                INSERT INTO knowledge_base_articles (organization_id, title, slug, content, summary, category, status, author_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (ORG_ID, title, title.lower().replace(' ', '-'), content, summary, category, 'published', 1, datetime.now() - timedelta(days=random.randint(30, 180))))
        
        # Create support tickets
        tickets_data = []
        for i in range(50):
            ticket_data = (
                f"TKT-{i+1:04d}",
                ORG_ID,
                f"Support Request #{i+1}",
                f"Customer needs assistance with {random.choice(['IT AMC', 'Cybersecurity', 'Infrastructure', 'ELV Systems', 'AV Solutions'])}",
                random.choice(["low", "medium", "high", "urgent"]),
                random.choice(["open", "in_progress", "resolved", "closed"]),
                random.choice(["IT Support", "Cybersecurity", "Infrastructure", "ELV Systems", "AV Solutions"]),
                f"customer{i+1}@example.com",
                f"Customer {i+1}",
                random.randint(1, 5),  # assigned_to_id
                datetime.now() - timedelta(days=random.randint(1, 90))
            )
            tickets_data.append(ticket_data)
        
        self.cursor.executemany("""
            INSERT INTO support_tickets (ticket_number, organization_id, title, description, priority, status, category, customer_email, customer_name, assigned_to_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, tickets_data)
        
        print("✅ Support tickets created")
        return True
    
    def seed_telephony_data(self):
        """Create telephony and call center data"""
        print("\n📞 Creating Telephony Data...")
        
        # Create PBX providers
        providers_data = [
            (ORG_ID, 1, "Asterisk PBX", "asterisk", "Main Asterisk PBX Server", "192.168.1.100", 8088, True),
            (ORG_ID, 1, "FreePBX System", "freepbx", "FreePBX Call Center System", "192.168.1.101", 8088, True)
        ]
        
        for org_id, created_by, name, provider_type, display_name, host, port, is_active in providers_data:
            self.cursor.execute("""
                INSERT INTO pbx_providers (organization_id, created_by, name, provider_type, display_name, host, port, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (org_id, created_by, name, provider_type, display_name, host, port, is_active, datetime.now() - timedelta(days=30)))
        
        # Create call queues
        queues_data = [
            (ORG_ID, 1, "IT Support Queue", "IT support and maintenance calls", "100", "ringall", True),
            (ORG_ID, 1, "Sales Queue", "Sales and new business inquiries", "101", "ringall", True)
        ]
        
        for org_id, provider_id, name, description, queue_number, strategy, is_active in queues_data:
            self.cursor.execute("""
                INSERT INTO call_queues (organization_id, provider_id, name, description, queue_number, strategy, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (org_id, provider_id, name, description, queue_number, strategy, is_active, datetime.now() - timedelta(days=30)))
        
        # Create calls data
        calls_data = []
        for i in range(100):
            call_data = (
                ORG_ID,
                1,  # provider_id
                f"call_{i+1:06d}",
                f"+971{random.randint(501000000, 599999999)}",
                f"Customer {random.randint(1, 50)}",
                random.choice(["inbound", "outbound", "internal"]),
                random.choice(["ringing", "answered", "completed", "busy"]),
                random.randint(1, 5),  # agent_id
                random.randint(1, 2),  # queue_id
                random.randint(1, 20),  # contact_id
                datetime.now() - timedelta(days=random.randint(1, 30))
            )
            calls_data.append(call_data)
        
        self.cursor.executemany("""
            INSERT INTO calls (organization_id, provider_id, unique_id, caller_id, caller_name, direction, status, agent_id, queue_id, contact_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, calls_data)
        
        print("✅ Telephony data created")
        return True
    
    def seed_chat_data(self):
        """Create chat rooms and messages"""
        print("\n💬 Creating Chat Data...")
        
        # Create chat rooms
        rooms_data = [
            (ORG_ID, 1, "General Discussion", "general", True),
            (ORG_ID, 1, "IT Support Team", "support", True),
            (ORG_ID, 1, "Sales Team", "sales", True)
        ]
        
        for org_id, created_by_id, name, room_type, is_active in rooms_data:
            self.cursor.execute("""
                INSERT INTO chat_rooms (organization_id, created_by_id, name, room_type, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (org_id, created_by_id, name, room_type, is_active, datetime.now() - timedelta(days=random.randint(30, 180))))
        
        # Create chat messages
        messages_data = []
        sample_messages = [
            "Good morning team! How are we doing today?",
            "Has anyone heard back from the Dubai Municipality project?",
            "The cybersecurity assessment for Emirates NBD is complete",
            "Need help with the Emaar Properties infrastructure setup",
            "Client meeting went well, they're interested in our ELV solutions"
        ]
        
        for room_id in range(1, 4):
            for i in range(20):  # 20 messages per room
                message_data = (
                    room_id,
                    random.randint(1, 5),  # sender_id
                    random.choice(sample_messages),
                    "text",
                    datetime.now() - timedelta(days=random.randint(1, 90))
                )
                messages_data.append(message_data)
        
        self.cursor.executemany("""
            INSERT INTO chat_messages (room_id, sender_id, content, message_type, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, messages_data)
        
        print("✅ Chat data created")
        return True
    
    def run_essential_seeding(self):
        """Run all essential seeding operations"""
        print("🚀 Starting Essential Demo Data Seeding for NeuraCRM")
        print("=" * 60)
        print(f"Target: The Node Information Technology LLC (Org ID: {ORG_ID})")
        print(f"Database: Railway PostgreSQL")
        print("=" * 60)
        
        try:
            self.connect()
            
            operations = [
                self.seed_organization_and_users,
                self.seed_contacts_and_leads,
                self.seed_deals_and_stages,
                self.seed_support_tickets,
                self.seed_telephony_data,
                self.seed_chat_data
            ]
            
            for operation in operations:
                if not operation():
                    print(f"❌ Operation failed: {operation.__name__}")
                    return False
            
            print("\n🎉 Essential Demo Data Seeding Completed Successfully!")
            print("=" * 60)
            print("✅ NeuraCRM now has realistic demo data for:")
            print("   👥 Contacts and Leads")
            print("   💼 Deals and Pipeline")
            print("   🎧 Customer Support")
            print("   📞 Call Center & Telephony")
            print("   💬 Chat & Communication")
            print("=" * 60)
            print("🚀 Ready for comprehensive demonstration!")
            
            return True
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            return False
        finally:
            self.close()

def main():
    """Main function to run essential seeding"""
    seeder = EssentialDataSeeder()
    success = seeder.run_essential_seeding()
    
    if success:
        print("\n✅ Demo data seeding completed successfully!")
        print("You can now showcase NeuraCRM features with realistic data.")
    else:
        print("\n❌ Demo data seeding failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
