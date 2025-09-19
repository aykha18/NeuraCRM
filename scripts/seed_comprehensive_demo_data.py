#!/usr/bin/env python3
"""
Comprehensive Demo Data Seeder for NeuraCRM
==========================================

This script creates realistic seed data for The Node Information Technology LLC
to showcase all advanced features of NeuraCRM including:

- Predictive Analytics & Forecasting
- Sentiment Analysis
- Customer Segmentation
- Advanced Financial Management
- Customer Support & Knowledge Base
- Call Center & Telephony
- Chat & Communication
- Customer Accounts & Success

Usage:
    python scripts/seed_comprehensive_demo_data.py

Target: Railway Database - Organization ID 1
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal

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

class ComprehensiveDataSeeder:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.batch_size = 100
        
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
    
    def execute_batch(self, query, data_list, description):
        """Execute batch insert with progress tracking"""
        try:
            print(f"📊 {description}...")
            total = len(data_list)
            
            for i in range(0, total, self.batch_size):
                batch = data_list[i:i + self.batch_size]
                self.cursor.executemany(query, batch)
                progress = min(i + self.batch_size, total)
                print(f"   ✅ {progress}/{total} records processed")
            
            print(f"✅ {description} completed: {total} records")
            return True
        except Exception as e:
            print(f"❌ Error in {description}: {e}")
            return False
    
    def seed_organizations_and_users(self):
        """Create organization and users for The Node IT"""
        print("\n🏢 Creating Organization and Users...")
        
        # Create organization if not exists
        self.cursor.execute("""
            INSERT INTO organizations (id, name, domain, settings, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                domain = EXCLUDED.domain,
                settings = EXCLUDED.settings
        """, (
            ORG_ID,
            "The Node Information Technology LLC",
            "nodeit.com",
            json.dumps({
                "industry": "IT Services",
                "size": "50-100 employees",
                "timezone": "Asia/Dubai",
                "currency": "AED",
                "features": ["telephony", "forecasting", "segmentation", "support"]
            }),
            datetime.now() - timedelta(days=365)
        ))
        
        # Create users for The Node IT
        users_data = [
            (1, "Ahmed Al-Rashid", "ahmed.rashid@nodeit.com", "admin", ORG_ID),
            (2, "Sarah Johnson", "sarah.johnson@nodeit.com", "manager", ORG_ID),
            (3, "Mohammed Hassan", "mohammed.hassan@nodeit.com", "agent", ORG_ID),
            (4, "Fatima Al-Zahra", "fatima.alzahra@nodeit.com", "agent", ORG_ID),
            (5, "David Chen", "david.chen@nodeit.com", "agent", ORG_ID),
            (6, "Aisha Mohammed", "aisha.mohammed@nodeit.com", "support", ORG_ID),
            (7, "Omar Al-Mansouri", "omar.mansouri@nodeit.com", "support", ORG_ID),
            (8, "Lisa Wang", "lisa.wang@nodeit.com", "sales", ORG_ID),
            (9, "Khalid Al-Suwaidi", "khalid.suwaidi@nodeit.com", "sales", ORG_ID),
            (10, "Emily Rodriguez", "emily.rodriguez@nodeit.com", "manager", ORG_ID)
        ]
        
        for user_id, name, email, role, org_id in users_data:
            self.cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, role, organization_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    role = EXCLUDED.role
            """, (user_id, name, email, "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J1Jpz6VqO", role, org_id, datetime.now() - timedelta(days=300)))
        
        print("✅ Organization and users created successfully")
        return True
    
    def seed_contacts_and_leads(self):
        """Create realistic contacts and leads for IT services business"""
        print("\n👥 Creating Contacts and Leads...")
        
        # IT Industry contacts - using actual schema columns
        contacts_data = []
        leads_data = []
        
        companies = [
            "Dubai Municipality", "Emirates NBD", "ADNOC", "Emaar Properties", 
            "Al Futtaim Group", "Dubai Airports", "Dubai Health Authority", 
            "DEWA", "RTA", "Dubai Police", "Abu Dhabi Investment Authority", 
            "Mubadala", "Aldar Properties", "First Abu Dhabi Bank", "Dubai Islamic Bank"
        ]
        
        contact_id = 1
        lead_id = 1
        
        for company in companies:
            # Create 2-3 contacts per company
            for i in range(random.randint(2, 3)):
                contact_data = (
                    f"Contact {contact_id} - {company}",
                    f"contact{contact_id}@{company.lower().replace(' ', '')}.com",
                    f"+971 {random.randint(50, 59)}{random.randint(1000000, 9999999)}",
                    company,
                    random.randint(1, 10),  # owner_id
                    datetime.now() - timedelta(days=random.randint(30, 365)),
                    ORG_ID
                )
                contacts_data.append(contact_data)
                
                # Create leads for some contacts
                if random.random() < 0.7:  # 70% of contacts become leads
                    services = [
                        "IT Annual Maintenance Contract (AMC)",
                        "Cybersecurity Solutions", 
                        "Digital Infrastructure Setup",
                        "ELV Systems Implementation",
                        "Audio-Visual Solutions",
                        "Website Development"
                    ]
                    
                    lead_data = (
                        f"{random.choice(services)} - {company}",
                        contact_id,
                        random.randint(1, 10),  # owner_id
                        random.choice(["new", "contacted", "qualified", "proposal"]),
                        random.choice(["website", "referral", "cold_call", "email"]),
                        datetime.now() - timedelta(days=random.randint(1, 90)),
                        random.randint(60, 95),  # score
                        datetime.now() - timedelta(hours=random.randint(1, 24)),  # score_updated_at
                        "High engagement, IT budget available, decision maker identified",
                        random.uniform(0.8, 0.95),  # score_confidence
                        ORG_ID
                    )
                    leads_data.append(lead_data)
                    lead_id += 1
                
                contact_id += 1
        
        # Batch insert contacts
        self.execute_batch("""
            INSERT INTO contacts (name, email, phone, company, owner_id, created_at, organization_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, contacts_data, "Creating contacts")
        
        # Batch insert leads
        self.execute_batch("""
            INSERT INTO leads (title, contact_id, owner_id, status, source, created_at, score, score_updated_at, score_factors, score_confidence, organization_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, leads_data, "Creating leads")
        
        return True
    
    def seed_deals_and_stages(self):
        """Create deals and pipeline stages"""
        print("\n💼 Creating Deals and Pipeline...")
        
        # Create stages - using actual schema columns
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
        
        # Create deals
        deals_data = []
        
        # Get some leads for deals
        self.cursor.execute("SELECT id, title FROM leads WHERE organization_id = %s LIMIT 30", (ORG_ID,))
        leads = self.cursor.fetchall()
        
        for lead_id, lead_title in leads:
            # Create deals from leads
            stage_id = random.choice([1, 2, 3, 4, 5, 6])
            actual_value = random.randint(50000, 500000)
            
            deal_data = (
                lead_title.replace(" - ", " Deal - "),
                actual_value,
                random.randint(1, 10),  # owner_id
                stage_id,
                f"Deal for {lead_title}",
                datetime.now() - timedelta(days=random.randint(1, 180)),
                datetime.now() - timedelta(days=random.randint(1, 30)) if stage_id in [5, 6] else None,  # closed_at
                random.randint(1, 50),  # contact_id
                ORG_ID,
                "active" if stage_id not in [5, 6] else ("won" if stage_id == 5 else "lost"),
                "Competitive pricing" if stage_id == 5 else "Budget constraints" if stage_id == 6 else None
            )
            deals_data.append(deal_data)
        
        # Batch insert deals
        self.execute_batch("""
            INSERT INTO deals (title, value, owner_id, stage_id, description, created_at, closed_at, contact_id, organization_id, status, outcome_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, deals_data, "Creating deals")
        
        return True
    
    def seed_customer_accounts(self):
        """Create customer accounts for won deals"""
        print("\n🏦 Creating Customer Accounts...")
        
        # Get won deals
        self.cursor.execute("""
            SELECT id, title, value, owner_id FROM deals 
            WHERE organization_id = %s AND stage_id = 5
        """, (ORG_ID,))
        won_deals = self.cursor.fetchall()
        
        accounts_data = []
        
        for deal_id, title, value, owner_id in won_deals:
            account_data = (
                deal_id,
                f"Account-{deal_id:04d}",
                random.randint(1, 50),  # contact_id
                random.choice(["standard", "premium", "enterprise"]),
                random.choice(["pending", "in_progress", "completed"]),
                random.randint(1, 10),  # success_manager_id
                random.uniform(70, 95),  # health_score
                random.choice(["low", "medium", "high"]),  # engagement_level
                datetime.now() - timedelta(days=random.randint(1, 90)),
                datetime.now() - timedelta(days=random.randint(1, 30))
            )
            accounts_data.append(account_data)
        
        self.execute_batch("""
            INSERT INTO customer_accounts (deal_id, account_name, contact_id, account_type, onboarding_status, success_manager_id, health_score, engagement_level, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, accounts_data, "Creating customer accounts")
        
        return True
    
    def seed_financial_data(self):
        """Create invoices, payments, and revenue data"""
        print("\n💰 Creating Financial Data...")
        
        # Get customer accounts
        self.cursor.execute("SELECT id, deal_id FROM customer_accounts WHERE id <= 20")
        accounts = self.cursor.fetchall()
        
        invoices_data = []
        payments_data = []
        revenue_data = []
        
        invoice_id = 1
        payment_id = 1
        revenue_id = 1
        
        for account_id, deal_id in accounts:
            # Create 2-4 invoices per account
            for i in range(random.randint(2, 4)):
                amount = random.randint(10000, 100000)
                status = random.choice(["draft", "sent", "paid", "overdue"])
                
                invoice_data = (
                    invoice_id,
                    f"INV-{invoice_id:06d}",
                    amount,
                    status,
                    "AED",
                    account_id,
                    random.randint(1, 10),  # created_by
                    ORG_ID,
                    datetime.now() - timedelta(days=random.randint(1, 120))
                )
                invoices_data.append(invoice_data)
                
                # Create payments for paid invoices
                if status == "paid":
                    payment_data = (
                        payment_id,
                        amount,
                        "AED",
                        "bank_transfer",
                        f"Payment for invoice INV-{invoice_id:06d}",
                        invoice_id,
                        ORG_ID,
                        datetime.now() - timedelta(days=random.randint(1, 30))
                    )
                    payments_data.append(payment_data)
                    
                    # Create revenue record
                    revenue_data.append((
                        revenue_id,
                        amount,
                        "AED",
                        "service_revenue",
                        f"Revenue from {account_id}",
                        invoice_id,
                        ORG_ID,
                        datetime.now() - timedelta(days=random.randint(1, 30))
                    ))
                    payment_id += 1
                    revenue_id += 1
                
                invoice_id += 1
        
        # Batch insert financial data
        self.execute_batch("""
            INSERT INTO invoices (id, invoice_number, amount, status, currency, account_id, created_by, organization_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                invoice_number = EXCLUDED.invoice_number,
                amount = EXCLUDED.amount
        """, invoices_data, "Creating invoices")
        
        self.execute_batch("""
            INSERT INTO payments (id, amount, currency, payment_method, description, invoice_id, organization_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                amount = EXCLUDED.amount,
                payment_method = EXCLUDED.payment_method
        """, payments_data, "Creating payments")
        
        self.execute_batch("""
            INSERT INTO revenue (id, amount, currency, revenue_type, description, invoice_id, organization_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                amount = EXCLUDED.amount,
                revenue_type = EXCLUDED.revenue_type
        """, revenue_data, "Creating revenue records")
        
        return True
    
    def seed_support_data(self):
        """Create support tickets, knowledge base, and analytics"""
        print("\n🎧 Creating Support Data...")
        
        # Create knowledge base articles
        kb_articles_data = [
            (1, "IT AMC Support Guide", "Complete guide for IT Annual Maintenance Contract support", "published", "IT Services", "Comprehensive guide covering all aspects of IT AMC support services..."),
            (2, "Cybersecurity Best Practices", "Essential cybersecurity practices for enterprise clients", "published", "Cybersecurity", "Detailed cybersecurity guidelines including endpoint protection and email security..."),
            (3, "Digital Infrastructure Setup", "Step-by-step guide for digital infrastructure implementation", "published", "Infrastructure", "Complete guide for setting up servers, storage, and email archival systems..."),
            (4, "ELV Systems Troubleshooting", "Common issues and solutions for ELV systems", "published", "ELV Systems", "Troubleshooting guide for door access control and IP phone systems..."),
            (5, "AV Solutions Configuration", "Audio-visual solutions setup and configuration guide", "published", "AV Solutions", "Guide for meeting room solutions, interactive displays, and video wall systems..."),
            (6, "Website Development Process", "Our website development methodology and process", "published", "Digital Media", "Detailed process for website development and IVR voice recording services...")
        ]
        
        for article_data in kb_articles_data:
            self.cursor.execute("""
                INSERT INTO knowledge_base_articles (id, title, description, status, category, content, created_by, organization_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content
            """, (*article_data, 1, ORG_ID, datetime.now() - timedelta(days=random.randint(30, 180))))
        
        # Create support tickets
        tickets_data = []
        ticket_id = 1
        
        categories = ["IT Support", "Cybersecurity", "Infrastructure", "ELV Systems", "AV Solutions", "Website Issues"]
        priorities = ["low", "medium", "high", "urgent"]
        statuses = ["open", "in_progress", "resolved", "closed"]
        
        for i in range(100):
            ticket_data = (
                ticket_id,
                f"Ticket #{ticket_id:04d}",
                f"Support request for {random.choice(categories)}",
                random.choice(categories),
                random.choice(priorities),
                random.choice(statuses),
                random.randint(1, 50),  # contact_id
                random.randint(1, 10),  # assigned_to
                ORG_ID,
                datetime.now() - timedelta(days=random.randint(1, 90))
            )
            tickets_data.append(ticket_data)
            ticket_id += 1
        
        self.execute_batch("""
            INSERT INTO support_tickets (id, title, description, category, priority, status, contact_id, assigned_to, organization_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description
        """, tickets_data, "Creating support tickets")
        
        return True
    
    def seed_telephony_data(self):
        """Create telephony and call center data"""
        print("\n📞 Creating Telephony Data...")
        
        # Create PBX providers
        pbx_providers_data = [
            (1, ORG_ID, 1, "Asterisk PBX", "asterisk", "Main Asterisk PBX Server", "192.168.1.100", 8088, True),
            (2, ORG_ID, 1, "FreePBX System", "freepbx", "FreePBX Call Center System", "192.168.1.101", 8088, True),
            (3, ORG_ID, 1, "3CX Phone System", "3cx", "3CX Professional Phone System", "192.168.1.102", 5000, True)
        ]
        
        for provider_data in pbx_providers_data:
            self.cursor.execute("""
                INSERT INTO pbx_providers (id, organization_id, created_by, name, provider_type, display_name, host, port, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    host = EXCLUDED.host
            """, (*provider_data, datetime.now() - timedelta(days=30)))
        
        # Create call queues
        call_queues_data = [
            (1, ORG_ID, 1, "IT Support Queue", "IT support and maintenance calls", "100", "ringall", True),
            (2, ORG_ID, 1, "Cybersecurity Queue", "Security-related support calls", "101", "fewestcalls", True),
            (3, ORG_ID, 1, "Sales Queue", "Sales and new business inquiries", "102", "ringall", True),
            (4, ORG_ID, 1, "Infrastructure Queue", "Infrastructure and setup support", "103", "leastrecent", True)
        ]
        
        for queue_data in call_queues_data:
            self.cursor.execute("""
                INSERT INTO call_queues (id, organization_id, provider_id, name, description, queue_number, strategy, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    queue_number = EXCLUDED.queue_number
            """, (*queue_data, datetime.now() - timedelta(days=30)))
        
        # Create calls data
        calls_data = []
        call_id = 1
        
        for i in range(200):
            call_data = (
                call_id,
                ORG_ID,
                random.randint(1, 3),  # provider_id
                f"call_{call_id:06d}",
                f"+971{random.randint(501000000, 599999999)}",  # caller_id
                f"Customer {random.randint(1, 50)}",
                random.choice(["inbound", "outbound", "internal"]),
                random.choice(["ringing", "answered", "completed", "busy", "no_answer"]),
                random.randint(1, 10),  # agent_id
                random.randint(1, 4),   # queue_id
                random.randint(1, 50),  # contact_id
                datetime.now() - timedelta(days=random.randint(1, 30))
            )
            calls_data.append(call_data)
            call_id += 1
        
        self.execute_batch("""
            INSERT INTO calls (id, organization_id, provider_id, unique_id, caller_id, caller_name, direction, status, agent_id, queue_id, contact_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                unique_id = EXCLUDED.unique_id,
                caller_id = EXCLUDED.caller_id
        """, calls_data, "Creating calls")
        
        return True
    
    def seed_chat_data(self):
        """Create chat rooms and messages"""
        print("\n💬 Creating Chat Data...")
        
        # Create chat rooms
        chat_rooms_data = [
            (1, ORG_ID, "General Discussion", "general", True),
            (2, ORG_ID, "IT Support Team", "support", True),
            (3, ORG_ID, "Sales Team", "sales", True),
            (4, ORG_ID, "Cybersecurity Team", "security", True),
            (5, ORG_ID, "Management", "management", True)
        ]
        
        for room_data in chat_rooms_data:
            self.cursor.execute("""
                INSERT INTO chat_rooms (id, organization_id, name, room_type, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    room_type = EXCLUDED.room_type
            """, (*room_data, datetime.now() - timedelta(days=random.randint(30, 180))))
        
        # Create chat messages
        messages_data = []
        message_id = 1
        
        sample_messages = [
            "Good morning team! How are we doing today?",
            "Has anyone heard back from the Dubai Municipality project?",
            "The cybersecurity assessment for Emirates NBD is complete",
            "Need help with the Emaar Properties infrastructure setup",
            "Client meeting went well, they're interested in our ELV solutions",
            "Reminder: Team meeting at 3 PM today",
            "The ADNOC project is progressing smoothly",
            "Need to update the knowledge base with new troubleshooting steps",
            "Customer feedback on our AV solutions has been excellent",
            "Sales targets for this quarter are looking good"
        ]
        
        for room_id in range(1, 6):
            for i in range(50):  # 50 messages per room
                message_data = (
                    message_id,
                    room_id,
                    random.randint(1, 10),  # user_id
                    random.choice(sample_messages),
                    "text",
                    datetime.now() - timedelta(days=random.randint(1, 90))
                )
                messages_data.append(message_data)
                message_id += 1
        
        self.execute_batch("""
            INSERT INTO chat_messages (id, room_id, user_id, message, message_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                message = EXCLUDED.message,
                message_type = EXCLUDED.message_type
        """, messages_data, "Creating chat messages")
        
        return True
    
    def seed_customer_segmentation(self):
        """Create customer segments and analytics"""
        print("\n📊 Creating Customer Segmentation Data...")
        
        # Create customer segments
        segments_data = [
            (1, ORG_ID, 1, "Enterprise Clients", "Large enterprise customers with complex IT needs", "behavioral", 
             {"min_deal_value": 100000, "company_size": "enterprise", "services": ["IT AMC", "Cybersecurity"]}, 
             True, True, datetime.now() - timedelta(days=60)),
            (2, ORG_ID, 1, "Government Sector", "Government and public sector organizations", "demographic",
             {"sector": "government", "location": "UAE", "priority": "high"}, 
             True, True, datetime.now() - timedelta(days=45)),
            (3, ORG_ID, 1, "SMB Technology Adopters", "Small to medium businesses adopting new technology", "behavioral",
             {"company_size": ["small", "medium"], "tech_adoption": "high", "budget_range": "10000-50000"},
             True, True, datetime.now() - timedelta(days=30)),
            (4, ORG_ID, 1, "Cybersecurity Focused", "Clients primarily interested in security solutions", "transactional",
             {"primary_service": "cybersecurity", "security_priority": "high"},
             True, True, datetime.now() - timedelta(days=20))
        ]
        
        for segment_data in segments_data:
            self.cursor.execute("""
                INSERT INTO customer_segments (id, organization_id, created_by, name, description, segment_type, criteria, is_active, is_auto_updated, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    criteria = EXCLUDED.criteria
            """, segment_data)
        
        # Create segment members
        segment_members_data = []
        member_id = 1
        
        for segment_id in range(1, 5):
            for contact_id in range(1, 21):  # 20 members per segment
                member_data = (
                    member_id,
                    segment_id,
                    contact_id,
                    random.uniform(0.6, 1.0),  # membership_score
                    random.uniform(0.5, 0.9),  # engagement_score
                    datetime.now() - timedelta(days=random.randint(1, 60))
                )
                segment_members_data.append(member_data)
                member_id += 1
        
        self.execute_batch("""
            INSERT INTO customer_segment_members (id, segment_id, contact_id, membership_score, segment_engagement_score, added_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                membership_score = EXCLUDED.membership_score,
                segment_engagement_score = EXCLUDED.segment_engagement_score
        """, segment_members_data, "Creating segment members")
        
        return True
    
    def seed_forecasting_data(self):
        """Create forecasting models and results"""
        print("\n🔮 Creating Forecasting Data...")
        
        # Create forecasting models
        models_data = [
            (1, ORG_ID, 1, "Revenue Forecasting Model", "Predicts monthly revenue based on historical data", "revenue", "deals", "ARIMA", "12_months", "6_months", True, datetime.now() - timedelta(days=30)),
            (2, ORG_ID, 1, "Pipeline Forecasting", "Forecasts deal pipeline progression", "pipeline", "deals", "Prophet", "6_months", "3_months", True, datetime.now() - timedelta(days=25)),
            (3, ORG_ID, 1, "Customer Growth Model", "Predicts customer acquisition and growth", "customer_growth", "contacts", "Linear_Regression", "24_months", "12_months", True, datetime.now() - timedelta(days=20)),
            (4, ORG_ID, 1, "Churn Prediction Model", "Predicts customer churn probability", "churn", "customer_accounts", "Exponential_Smoothing", "12_months", "3_months", True, datetime.now() - timedelta(days=15))
        ]
        
        for model_data in models_data:
            self.cursor.execute("""
                INSERT INTO forecasting_models (id, organization_id, created_by, name, description, model_type, data_source, model_algorithm, training_data_period, forecast_horizon, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description
            """, model_data)
        
        # Create forecast results
        forecast_results_data = []
        result_id = 1
        
        for model_id in range(1, 5):
            for month in range(1, 13):  # 12 months of forecasts
                forecast_date = datetime.now() + timedelta(days=month * 30)
                forecast_value = random.randint(100000, 500000)
                
                result_data = (
                    result_id,
                    model_id,
                    f"forecast_{month}",
                    f"month_{month}",
                    forecast_date,
                    forecast_value,
                    forecast_value * 0.9,  # lower bound
                    forecast_value * 1.1,  # upper bound
                    random.uniform(0.8, 0.95),  # accuracy_score
                    random.choice(["upward", "downward", "stable"]),  # trend
                    datetime.now() - timedelta(days=random.randint(1, 30))
                )
                forecast_results_data.append(result_data)
                result_id += 1
        
        self.execute_batch("""
            INSERT INTO forecast_results (id, model_id, forecast_type, forecast_period, forecast_date, forecasted_value, confidence_interval_lower, confidence_interval_upper, accuracy_score, trend_direction, generated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                forecasted_value = EXCLUDED.forecasted_value,
                accuracy_score = EXCLUDED.accuracy_score
        """, forecast_results_data, "Creating forecast results")
        
        return True
    
    def seed_sentiment_analysis_data(self):
        """Create sentiment analysis data for support tickets and chat"""
        print("\n😊 Creating Sentiment Analysis Data...")
        
        # Create sentiment analysis for support tickets
        sentiment_data = []
        sentiment_id = 1
        
        # Get support tickets
        self.cursor.execute("SELECT id, description FROM support_tickets WHERE organization_id = %s LIMIT 50", (ORG_ID,))
        tickets = self.cursor.fetchall()
        
        for ticket_id, description in tickets:
            # Generate realistic sentiment based on ticket content
            if any(word in description.lower() for word in ["urgent", "critical", "broken", "failed"]):
                sentiment_score = random.uniform(-0.8, -0.3)
                sentiment_label = "negative"
            elif any(word in description.lower() for word in ["thanks", "great", "excellent", "solved"]):
                sentiment_score = random.uniform(0.3, 0.8)
                sentiment_label = "positive"
            else:
                sentiment_score = random.uniform(-0.2, 0.2)
                sentiment_label = "neutral"
            
            sentiment_data.append((
                sentiment_id,
                "support_ticket",
                ticket_id,
                sentiment_score,
                sentiment_label,
                datetime.now() - timedelta(days=random.randint(1, 30))
            ))
            sentiment_id += 1
        
        # Create sentiment analysis for chat messages
        self.cursor.execute("SELECT id, message FROM chat_messages WHERE room_id <= 3 LIMIT 100")
        chat_messages = self.cursor.fetchall()
        
        for message_id, message in chat_messages:
            if any(word in message.lower() for word in ["good", "great", "excellent", "awesome"]):
                sentiment_score = random.uniform(0.2, 0.7)
                sentiment_label = "positive"
            elif any(word in message.lower() for word in ["problem", "issue", "help", "urgent"]):
                sentiment_score = random.uniform(-0.5, 0.1)
                sentiment_label = "neutral"
            else:
                sentiment_score = random.uniform(-0.1, 0.3)
                sentiment_label = "neutral"
            
            sentiment_data.append((
                sentiment_id,
                "chat_message",
                message_id,
                sentiment_score,
                sentiment_label,
                datetime.now() - timedelta(days=random.randint(1, 30))
            ))
            sentiment_id += 1
        
        # Note: Assuming sentiment_analysis table exists
        # If not, we'll create a simple activity-based sentiment tracking
        activities_data = []
        activity_id = 1
        
        for sentiment_id, source_type, source_id, score, label, created_at in sentiment_data:
            activities_data.append((
                activity_id,
                f"Sentiment Analysis - {source_type}",
                f"Analyzed {source_type} #{source_id} - Sentiment: {label} (Score: {score:.2f})",
                source_type,
                source_id,
                random.randint(1, 10),  # user_id
                ORG_ID,
                created_at
            ))
            activity_id += 1
        
        self.execute_batch("""
            INSERT INTO activities (id, type, description, entity_type, entity_id, user_id, organization_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                type = EXCLUDED.type,
                description = EXCLUDED.description
        """, activities_data, "Creating sentiment analysis activities")
        
        return True
    
    def seed_call_analytics(self):
        """Create call analytics and performance data"""
        print("\n📈 Creating Call Analytics...")
        
        analytics_data = []
        analytics_id = 1
        
        # Generate daily analytics for the last 30 days
        for day in range(30):
            date = datetime.now().date() - timedelta(days=day)
            
            for hour in range(24):
                for provider_id in range(1, 4):
                    for queue_id in range(1, 5):
                        analytics_data.append((
                            analytics_id,
                            ORG_ID,
                            date,
                            hour,
                            provider_id,
                            queue_id,
                            random.randint(0, 50),      # total_calls
                            random.randint(0, 45),      # answered_calls
                            random.randint(0, 10),      # abandoned_calls
                            random.randint(30, 300),    # avg_wait_time
                            random.randint(60, 1800),   # avg_talk_time
                            random.randint(10, 120),    # avg_hold_time
                            random.uniform(70, 95),     # service_level
                            random.uniform(60, 90),     # first_call_resolution
                            random.uniform(3.5, 5.0),   # customer_satisfaction
                            datetime.now() - timedelta(days=day)
                        ))
                        analytics_id += 1
        
        self.execute_batch("""
            INSERT INTO call_analytics (id, organization_id, date, hour, provider_id, queue_id, total_calls, answered_calls, abandoned_calls, avg_wait_time, avg_talk_time, avg_hold_time, service_level, first_call_resolution, customer_satisfaction, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                total_calls = EXCLUDED.total_calls,
                answered_calls = EXCLUDED.answered_calls
        """, analytics_data, "Creating call analytics")
        
        return True
    
    def run_comprehensive_seeding(self):
        """Run all seeding operations"""
        print("🚀 Starting Comprehensive Demo Data Seeding for NeuraCRM")
        print("=" * 60)
        print(f"Target: The Node Information Technology LLC (Org ID: {ORG_ID})")
        print(f"Database: Railway PostgreSQL")
        print("=" * 60)
        
        try:
            self.connect()
            
            # Run all seeding operations
            operations = [
                self.seed_organizations_and_users,
                self.seed_contacts_and_leads,
                self.seed_deals_and_stages,
                self.seed_customer_accounts,
                self.seed_financial_data,
                self.seed_support_data,
                self.seed_telephony_data,
                self.seed_chat_data,
                self.seed_customer_segmentation,
                self.seed_forecasting_data,
                self.seed_sentiment_analysis_data,
                self.seed_call_analytics
            ]
            
            for operation in operations:
                if not operation():
                    print(f"❌ Operation failed: {operation.__name__}")
                    return False
            
            print("\n🎉 Comprehensive Demo Data Seeding Completed Successfully!")
            print("=" * 60)
            print("✅ All NeuraCRM features now have realistic demo data:")
            print("   📊 Predictive Analytics & Forecasting")
            print("   😊 Sentiment Analysis")
            print("   👥 Customer Segmentation")
            print("   💰 Advanced Financial Management")
            print("   🎧 Customer Support & Knowledge Base")
            print("   📞 Call Center & Telephony")
            print("   💬 Chat & Communication")
            print("   🏦 Customer Accounts & Success")
            print("=" * 60)
            print("🚀 NeuraCRM is now ready for comprehensive demonstration!")
            
            return True
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            return False
        finally:
            self.close()

def main():
    """Main function to run comprehensive seeding"""
    seeder = ComprehensiveDataSeeder()
    success = seeder.run_comprehensive_seeding()
    
    if success:
        print("\n✅ Demo data seeding completed successfully!")
        print("You can now showcase all NeuraCRM features with realistic data.")
    else:
        print("\n❌ Demo data seeding failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
