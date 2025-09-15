"""
Generate realistic sample data for Predictive Analytics
Creates historical sales data, customer behavior patterns, and market trends
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.db import get_session_local
from api.models import Lead, Contact, Deal, User, Organization, Stage, Activity
from datetime import datetime, timedelta
import random
import json
from sqlalchemy import text

def generate_realistic_data():
    """Generate comprehensive realistic data for predictive analytics"""
    db = get_session_local()()
    
    try:
        print("🚀 Generating realistic data for Predictive Analytics...")
        
        # Get existing organizations and users
        organizations = db.query(Organization).all()
        users = db.query(User).all()
        stages = db.query(Stage).all()
        
        if not organizations or not users or not stages:
            print("❌ Need existing organizations, users, and stages first")
            return
        
        # Industry types for realistic company names
        industries = [
            "Technology", "Healthcare", "Finance", "Manufacturing", "Retail", 
            "Education", "Real Estate", "Consulting", "Media", "Automotive"
        ]
        
        company_suffixes = [
            "Corp", "Inc", "LLC", "Ltd", "Group", "Solutions", "Systems", 
            "Technologies", "Enterprises", "Partners", "Associates", "Consulting"
        ]
        
        # Generate realistic company names
        company_names = []
        for industry in industries:
            for suffix in company_suffixes[:3]:  # Limit to avoid too many
                company_names.append(f"{industry} {suffix}")
        
        # Add some specific realistic companies
        realistic_companies = [
            "Acme Technologies", "Global Solutions Inc", "Premier Healthcare Systems",
            "Advanced Manufacturing Corp", "Smart Retail Solutions", "EduTech Innovations",
            "Prime Real Estate Group", "Strategic Consulting Partners", "Digital Media Corp",
            "AutoTech Solutions", "Financial Services Group", "TechStart Ventures",
            "Healthcare Innovations", "Manufacturing Excellence", "Retail Dynamics",
            "Educational Systems", "Property Management Co", "Business Consulting",
            "Media Productions", "Automotive Solutions"
        ]
        
        company_names.extend(realistic_companies)
        
        # Generate contacts with realistic names
        first_names = [
            "John", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Ashley",
            "William", "Amanda", "James", "Jennifer", "Christopher", "Michelle", "Daniel",
            "Kimberly", "Matthew", "Lisa", "Anthony", "Nancy", "Mark", "Karen", "Donald",
            "Helen", "Steven", "Sandra", "Paul", "Donna", "Andrew", "Carol", "Joshua",
            "Ruth", "Kenneth", "Sharon", "Kevin", "Michelle", "Brian", "Laura", "George",
            "Sarah", "Edward", "Kimberly", "Ronald", "Deborah", "Timothy", "Dorothy"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
        ]
        
        # Generate realistic email domains
        email_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com",
            "business.org", "enterprise.net", "corporate.io", "solutions.com"
        ]
        
        # Generate deals with realistic values and patterns
        deal_values = [5000, 10000, 15000, 25000, 50000, 75000, 100000, 150000, 200000, 500000]
        deal_probabilities = [0.3, 0.25, 0.2, 0.15, 0.05, 0.03, 0.01, 0.005, 0.002, 0.001]
        
        # Generate data for the last 12 months
        start_date = datetime.now() - timedelta(days=365)
        
        print("📊 Generating contacts and leads...")
        
        # Generate 200 contacts with realistic data
        contacts_created = 0
        for i in range(200):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            company = random.choice(company_names)
            
            contact = Contact(
                name=f"{first_name} {last_name}",
                email=f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_domains)}",
                phone=f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                company=company,
                owner_id=random.choice(users).id,
                organization_id=random.choice(organizations).id,
                created_at=start_date + timedelta(days=random.randint(0, 365))
            )
            
            db.add(contact)
            contacts_created += 1
        
        db.commit()
        print(f"✅ Created {contacts_created} contacts")
        
        # Generate 300 leads with realistic patterns
        leads_created = 0
        lead_sources = ["Website", "Referral", "Cold Call", "Email Campaign", "Trade Show", "Social Media", "Partner"]
        lead_statuses = ["New", "Contacted", "Qualified", "Proposal Sent", "Negotiation", "Won", "Lost"]
        
        for i in range(300):
            # Get a random contact
            contact = db.query(Contact).order_by(text("RANDOM()")).first()
            
            # Create realistic lead titles
            lead_titles = [
                f"Software Implementation for {contact.company}",
                f"Digital Transformation Project",
                f"Cloud Migration Services",
                f"Data Analytics Solution",
                f"Customer Management System",
                f"Process Automation Initiative",
                f"Security Assessment and Implementation",
                f"Mobile App Development",
                f"E-commerce Platform Setup",
                f"Business Intelligence Dashboard"
            ]
            
            lead = Lead(
                title=random.choice(lead_titles),
                status=random.choice(lead_statuses),
                source=random.choice(lead_sources),
                score=random.randint(20, 95),  # Realistic lead scores
                contact_id=contact.id,
                owner_id=random.choice(users).id,
                organization_id=contact.organization_id,
                created_at=start_date + timedelta(days=random.randint(0, 365))
            )
            
            db.add(lead)
            leads_created += 1
        
        db.commit()
        print(f"✅ Created {leads_created} leads")
        
        # Generate 150 deals with realistic patterns
        deals_created = 0
        deal_titles = [
            "Enterprise Software License",
            "Cloud Infrastructure Setup",
            "Digital Marketing Campaign",
            "Data Migration Project",
            "Security Implementation",
            "Mobile App Development",
            "E-commerce Platform",
            "Business Process Automation",
            "Analytics Dashboard",
            "Customer Support System"
        ]
        
        for i in range(150):
            # Get a random contact
            contact = db.query(Contact).order_by(text("RANDOM()")).first()
            
            # Create deal with realistic value distribution
            value = random.choices(deal_values, weights=deal_probabilities)[0]
            
            # Add some variation to values
            value = int(value * random.uniform(0.8, 1.2))
            
            deal = Deal(
                title=random.choice(deal_titles),
                description=f"Comprehensive solution for {contact.company}",
                value=value,
                contact_id=contact.id,
                owner_id=random.choice(users).id,
                stage_id=random.choice(stages).id,
                organization_id=contact.organization_id,
                created_at=start_date + timedelta(days=random.randint(0, 365))
            )
            
            db.add(deal)
            deals_created += 1
        
        db.commit()
        print(f"✅ Created {deals_created} deals")
        
        # Generate activity data for realistic patterns
        print("📈 Generating activity patterns...")
        activities_created = 0
        
        activity_types = [
            "Email Sent", "Call Made", "Meeting Scheduled", "Proposal Sent",
            "Demo Completed", "Follow-up Call", "Contract Signed", "Payment Received"
        ]
        
        # Generate activities for the last 6 months
        for i in range(500):
            # Random date in last 6 months
            activity_date = datetime.now() - timedelta(days=random.randint(0, 180))
            
            # Get random lead or deal
            if random.choice([True, False]):
                entity = db.query(Lead).order_by(text("RANDOM()")).first()
                entity_type = "lead"
                entity_id = entity.id
            else:
                entity = db.query(Deal).order_by(text("RANDOM()")).first()
                entity_type = "deal"
                entity_id = entity.id
            
            activity = Activity(
                type=random.choice(activity_types),
                message=f"{random.choice(activity_types)} for {entity.title}",
                timestamp=activity_date,
                user_id=random.choice(users).id
            )
            
            db.add(activity)
            activities_created += 1
        
        db.commit()
        print(f"✅ Created {activities_created} activities")
        
        print("🎉 Realistic data generation complete!")
        print(f"📊 Summary:")
        print(f"   - {contacts_created} contacts")
        print(f"   - {leads_created} leads")
        print(f"   - {deals_created} deals")
        print(f"   - {activities_created} activities")
        print(f"   - Data spans last 12 months")
        print(f"   - Realistic company names, emails, and values")
        
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    generate_realistic_data()
