#!/usr/bin/env python3
"""
Seed Railway Missing Data
========================

Creates comprehensive data for missing Railway modules:
- Financial Management (invoices, payments, revenue, reports)
- Customer Support queues
- Call Center queue members
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime, timedelta
import random

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def seed_missing_data():
    """Seed missing data for Railway modules"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # 1. SEED FINANCIAL MANAGEMENT DATA
        print("\n💰 SEEDING FINANCIAL MANAGEMENT DATA...")
        
        # Get some deals to create invoices for
        cursor.execute("SELECT id, title, value FROM deals WHERE organization_id = 1 AND value > 0 LIMIT 20")
        deals = cursor.fetchall()
        
        if deals:
            # Create invoices with correct schema
            invoice_ids = []
            for i, (deal_id, title, value) in enumerate(deals):
                issue_date = datetime.now() - timedelta(days=random.randint(1, 90))
                due_date = issue_date + timedelta(days=30)
                tax_rate = 0.05
                tax_amount = value * tax_rate
                total_amount = value + tax_amount
                paid_amount = random.choice([0, total_amount]) if random.random() > 0.3 else total_amount * 0.5
                balance_due = total_amount - paid_amount
                
                cursor.execute("""
                    INSERT INTO invoices (
                        invoice_number, deal_id, customer_account_id, organization_id,
                        issue_date, due_date, status, subtotal, tax_rate, tax_amount,
                        total_amount, paid_amount, balance_due, description, notes,
                        terms_conditions, created_by, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """, (
                    f"INV-{2025:04d}-{i+1:04d}",
                    deal_id,
                    random.randint(1, 3),  # customer_account_id
                    1,  # organization_id
                    issue_date,
                    due_date,
                    'paid' if paid_amount == total_amount else ('overdue' if balance_due > 0 and due_date < datetime.now() else 'pending'),
                    value,
                    tax_rate,
                    tax_amount,
                    total_amount,
                    paid_amount,
                    balance_due,
                    f"Invoice for {title}",
                    f"Payment terms: Net 30 days",
                    "Payment due within 30 days of invoice date",
                    16,  # created_by (user ID)
                    datetime.now(),
                    datetime.now()
                ))
                invoice_ids.append(cursor.fetchone()[0])
            
            print(f"  ✓ Created {len(invoice_ids)} invoices")
            
            # Create payments for paid invoices
            payment_count = 0
            for invoice_id in invoice_ids:
                cursor.execute("SELECT total_amount, paid_amount FROM invoices WHERE id = %s", (invoice_id,))
                total_amount, paid_amount = cursor.fetchone()
                
                if paid_amount > 0:
                    payment_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    
                    cursor.execute("""
                        INSERT INTO payments (
                            invoice_id, organization_id, payment_number, amount,
                            payment_date, payment_method, payment_reference,
                            status, notes, created_by, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        invoice_id,
                        1,  # organization_id
                        f"PAY-{random.randint(10000, 99999)}",
                        paid_amount,
                        payment_date,
                        random.choice(['credit_card', 'bank_transfer', 'check', 'cash']),
                        f"REF-{random.randint(1000, 9999)}",
                        'completed',
                        f"Payment for invoice {invoice_id}",
                        16,  # created_by
                        datetime.now(),
                        datetime.now()
                    ))
                    payment_count += 1
            
            print(f"  ✓ Created {payment_count} payments")
            
            # Create revenue records
            revenue_count = 0
            for invoice_id in invoice_ids:
                cursor.execute("SELECT total_amount, paid_amount FROM invoices WHERE id = %s AND paid_amount > 0", (invoice_id,))
                result = cursor.fetchone()
                
                if result:
                    total_amount, paid_amount = result
                    recognition_date = datetime.now() - timedelta(days=random.randint(1, 60))
                    
                    cursor.execute("""
                        INSERT INTO revenue (
                            invoice_id, deal_id, organization_id, amount,
                            recognition_date, recognition_type, recognition_period,
                            revenue_type, revenue_category, status, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        invoice_id,
                        random.choice([deal[0] for deal in deals]),
                        1,  # organization_id
                        paid_amount,
                        recognition_date,
                        'immediate',
                        'monthly',
                        'product_sales',
                        'software_licenses',
                        'recognized',
                        datetime.now(),
                        datetime.now()
                    ))
                    revenue_count += 1
            
            print(f"  ✓ Created {revenue_count} revenue records")
            
            # Create financial reports
            report_count = 0
            for month in range(6):  # Last 6 months
                report_date = datetime.now() - timedelta(days=30 * month)
                period_start = report_date.replace(day=1)
                period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                cursor.execute("""
                    INSERT INTO financial_reports (
                        organization_id, report_type, report_period, report_name,
                        revenue_data, payment_data, invoice_data, kpi_data,
                        status, generated_by, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    1,  # organization_id
                    'monthly',
                    f"{period_start.strftime('%Y-%m')}",
                    f"Monthly Financial Report - {period_start.strftime('%B %Y')}",
                    json.dumps({
                        "total_revenue": random.uniform(50000, 150000),
                        "product_sales": random.uniform(30000, 80000),
                        "services": random.uniform(20000, 70000),
                        "growth_rate": random.uniform(0.05, 0.25)
                    }),
                    json.dumps({
                        "total_payments": random.uniform(45000, 140000),
                        "payment_methods": {
                            "credit_card": random.uniform(20000, 60000),
                            "bank_transfer": random.uniform(15000, 50000),
                            "check": random.uniform(5000, 20000),
                            "cash": random.uniform(2000, 10000)
                        }
                    }),
                    json.dumps({
                        "total_invoices": random.randint(20, 80),
                        "paid_invoices": random.randint(15, 70),
                        "overdue_invoices": random.randint(1, 10),
                        "avg_invoice_amount": random.uniform(2000, 8000)
                    }),
                    json.dumps({
                        "gross_margin": random.uniform(0.6, 0.8),
                        "net_profit": random.uniform(10000, 75000),
                        "cash_flow": random.uniform(5000, 50000),
                        "customer_acquisition_cost": random.uniform(200, 800)
                    }),
                    'completed',
                    16,  # generated_by
                    datetime.now(),
                    datetime.now()
                ))
                report_count += 1
            
            print(f"  ✓ Created {report_count} financial reports")
        
        # 2. SEED CUSTOMER SUPPORT QUEUES
        print("\n🎧 SEEDING CUSTOMER SUPPORT QUEUES...")
        
        # Check if queues exist
        cursor.execute("SELECT COUNT(*) FROM support_queues")
        queue_count = cursor.fetchone()[0]
        
        if queue_count == 0:
            queues_data = [
                {
                    "name": "General Support",
                    "description": "General customer support inquiries",
                    "priority": "normal",
                    "sla_hours": 24,
                    "auto_assign": True,
                    "is_active": True
                },
                {
                    "name": "Technical Support",
                    "description": "Technical issues and troubleshooting",
                    "priority": "high",
                    "sla_hours": 4,
                    "auto_assign": True,
                    "is_active": True
                },
                {
                    "name": "Billing Support",
                    "description": "Billing and payment related inquiries",
                    "priority": "normal",
                    "sla_hours": 12,
                    "auto_assign": False,
                    "is_active": True
                },
                {
                    "name": "Enterprise Support",
                    "description": "Premium support for enterprise customers",
                    "priority": "urgent",
                    "sla_hours": 2,
                    "auto_assign": True,
                    "is_active": True
                }
            ]
            
            for queue_data in queues_data:
                cursor.execute("""
                    INSERT INTO support_queues (
                        name, description, priority, sla_hours,
                        auto_assign, is_active, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    queue_data["name"],
                    queue_data["description"],
                    queue_data["priority"],
                    queue_data["sla_hours"],
                    queue_data["auto_assign"],
                    queue_data["is_active"],
                    datetime.now()
                ))
            
            print(f"  ✓ Created {len(queues_data)} support queues")
        else:
            print(f"  ✓ Support queues already exist ({queue_count} queues)")
        
        # 3. SEED CALL CENTER QUEUE MEMBERS
        print("\n📞 SEEDING CALL CENTER QUEUE MEMBERS...")
        
        # Get existing call queues and users
        cursor.execute("SELECT id FROM call_queues")
        queue_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE organization_id = 1")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if queue_ids and user_ids:
            # Clear existing queue members
            cursor.execute("DELETE FROM call_queue_members")
            
            # Create queue members
            member_count = 0
            for queue_id in queue_ids:
                # Assign 2-4 users to each queue
                queue_users = random.sample(user_ids, min(len(user_ids), random.randint(2, 4)))
                
                for user_id in queue_users:
                    cursor.execute("""
                        INSERT INTO call_queue_members (
                            queue_id, user_id, extension_id, penalty,
                            paused, status, total_calls, answered_calls,
                            missed_calls, avg_talk_time, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        queue_id,
                        user_id,
                        random.randint(100, 999),  # extension number
                        random.randint(1, 10),     # penalty
                        False,                     # not paused
                        'logged_in',               # status
                        random.randint(10, 100),   # total calls
                        random.randint(8, 95),     # answered calls
                        random.randint(0, 20),     # missed calls
                        random.randint(120, 600),  # avg talk time in seconds
                        datetime.now(),
                        datetime.now()
                    ))
                    member_count += 1
            
            print(f"  ✓ Created {member_count} call queue members")
        else:
            print("  ❌ No call queues or users found to create queue members")
        
        print("\n" + "=" * 60)
        print("🎉 Railway missing data seeding completed successfully!")
        print("\nNow Railway should have:")
        print("✅ Financial Management: Invoices, payments, revenue, reports")
        print("✅ Customer Support: Complete queue system")
        print("✅ Call Center: Queue members assigned")
        print("✅ All modules should now display data instead of being blank")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding missing data: {e}")
        return False

if __name__ == "__main__":
    seed_missing_data()