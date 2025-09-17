#!/usr/bin/env python3
"""
CRM Integration Test
Tests AI integration with actual CRM data and functions
"""
import os
import asyncio
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Add backend to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.models import Base, User, Organization, Contact, Lead, Deal, Stage, EmailTemplate

# Load environment variables
load_dotenv()

class CRMIntegrationTest:
    """Test CRM integration with AI"""
    
    def __init__(self):
        self.setup_database()
        self.setup_ai_client()
        self.create_test_data()
    
    def setup_database(self):
        """Setup test database"""
        # Create test database
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        
        # Create session
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()
        
        print("✅ Test database setup complete")
    
    def setup_ai_client(self):
        """Setup AI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        self.client = AsyncOpenAI(api_key=api_key)
        print("✅ AI client setup complete")
    
    def create_test_data(self):
        """Create test CRM data"""
        # Create test organization
        self.test_org = Organization(
            id=1,
            name="Test Company",
            domain="testcompany.com"
        )
        self.db.add(self.test_org)
        
        # Create test user
        self.test_user = User(
            id=1,
            name="Test Sales Rep",
            email="test@testcompany.com",
            password_hash="test_hash",
            role="sales_rep",
            organization_id=1
        )
        self.db.add(self.test_user)
        
        # Create test stages
        self.stages = [
            Stage(id=1, name="Prospecting", order=1),
            Stage(id=2, name="Qualification", order=2),
            Stage(id=3, name="Proposal", order=3),
            Stage(id=4, name="Closed Won", order=4)
        ]
        for stage in self.stages:
            self.db.add(stage)
        
        # Create test contacts
        self.test_contacts = [
            Contact(
                id=1,
                name="John Smith",
                email="john@acmecorp.com",
                phone="555-0123",
                company="ACME Corp",
                owner_id=1,
                organization_id=1
            ),
            Contact(
                id=2,
                name="Sarah Johnson",
                email="sarah@techstart.com",
                phone="555-0456",
                company="TechStart Inc",
                owner_id=1,
                organization_id=1
            )
        ]
        for contact in self.test_contacts:
            self.db.add(contact)
        
        # Create test leads
        self.test_leads = [
            Lead(
                id=1,
                title="ACME Corp - Enterprise Software",
                contact_id=1,
                owner_id=1,
                organization_id=1,
                status="qualified",
                source="website",
                score=85
            ),
            Lead(
                id=2,
                title="TechStart - CRM Integration",
                contact_id=2,
                owner_id=1,
                organization_id=1,
                status="new",
                source="referral",
                score=65
            )
        ]
        for lead in self.test_leads:
            self.db.add(lead)
        
        # Create test deals
        self.test_deals = [
            Deal(
                id=1,
                title="ACME Corp - Enterprise License",
                value=50000.0,
                owner_id=1,
                stage_id=3,
                organization_id=1,
                contact_id=1
            ),
            Deal(
                id=2,
                title="TechStart - Basic Package",
                value=5000.0,
                owner_id=1,
                stage_id=2,
                organization_id=1,
                contact_id=2
            )
        ]
        for deal in self.test_deals:
            self.db.add(deal)
        
        # Create test email templates
        self.test_templates = [
            EmailTemplate(
                id=1,
                name="Welcome Email",
                category="welcome",
                subject="Welcome to {{contact.company}}, {{contact.name}}!",
                body="<p>Hi {{contact.name}},</p><p>Welcome to our services!</p>",
                created_by=1
            )
        ]
        for template in self.test_templates:
            self.db.add(template)
        
        self.db.commit()
        print("✅ Test data created successfully")
    
    async def test_crm_data_access(self):
        """Test CRM data access with AI"""
        print("\n🧪 Testing CRM Data Access...")
        
        try:
            # Test 1: Get lead context
            lead = self.db.query(Lead).filter(Lead.id == 1).first()
            contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
            
            lead_context = {
                "lead": {
                    "id": lead.id,
                    "title": lead.title,
                    "status": lead.status,
                    "score": lead.score
                },
                "contact": {
                    "name": contact.name,
                    "email": contact.email,
                    "company": contact.company
                }
            }
            
            # Use AI to analyze the lead
            analysis_prompt = f"""
            Analyze this lead and provide recommendations:
            
            Lead Data: {json.dumps(lead_context, indent=2)}
            
            Provide:
            1. Lead qualification assessment
            2. Next steps recommendation
            3. Follow-up strategy
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a sales expert. Analyze leads and provide actionable recommendations."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content and len(content) > 100:
                print("   ✅ Lead Analysis: PASS")
                print(f"   📝 Analysis length: {len(content)} characters")
            else:
                print("   ❌ Lead Analysis: FAIL")
                return False
            
            # Test 2: Get deal context
            deal = self.db.query(Deal).filter(Deal.id == 1).first()
            stage = self.db.query(Stage).filter(Stage.id == deal.stage_id).first()
            
            deal_context = {
                "deal": {
                    "id": deal.id,
                    "title": deal.title,
                    "value": deal.value,
                    "stage": stage.name
                },
                "contact": {
                    "name": contact.name,
                    "company": contact.company
                }
            }
            
            # Use AI to analyze the deal
            deal_prompt = f"""
            Analyze this deal and provide strategy:
            
            Deal Data: {json.dumps(deal_context, indent=2)}
            
            Provide:
            1. Deal health assessment
            2. Closing strategy
            3. Risk factors
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a deal strategy expert. Analyze deals and provide closing strategies."},
                    {"role": "user", "content": deal_prompt}
                ],
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content and len(content) > 100:
                print("   ✅ Deal Analysis: PASS")
                print(f"   📝 Analysis length: {len(content)} characters")
            else:
                print("   ❌ Deal Analysis: FAIL")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ CRM Data Access Test Failed: {str(e)}")
            return False
    
    async def test_email_personalization(self):
        """Test email personalization with CRM data"""
        print("\n🧪 Testing Email Personalization...")
        
        try:
            # Get template and contact data
            template = self.db.query(EmailTemplate).filter(EmailTemplate.id == 1).first()
            contact = self.db.query(Contact).filter(Contact.id == 1).first()
            
            # Create context for personalization
            context = {
                "contact": {
                    "name": contact.name,
                    "company": contact.company
                }
            }
            
            # Use AI to personalize the email
            personalization_prompt = f"""
            Personalize this email template with the provided context:
            
            Template Subject: {template.subject}
            Template Body: {template.body}
            Context: {json.dumps(context, indent=2)}
            
            Generate a personalized email that feels natural and professional.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert email personalization specialist. Create natural, personalized emails."},
                    {"role": "user", "content": personalization_prompt}
                ],
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            if content and contact.name in content and contact.company in content:
                print("   ✅ Email Personalization: PASS")
                print(f"   📝 Personalized email length: {len(content)} characters")
            else:
                print("   ❌ Email Personalization: FAIL")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Email Personalization Test Failed: {str(e)}")
            return False
    
    async def test_pipeline_analysis(self):
        """Test pipeline analysis with CRM data"""
        print("\n🧪 Testing Pipeline Analysis...")
        
        try:
            # Get pipeline data
            deals = self.db.query(Deal).all()
            stages = self.db.query(Stage).all()
            
            pipeline_data = {
                "total_deals": len(deals),
                "total_value": sum(deal.value or 0 for deal in deals),
                "stages": [
                    {
                        "name": stage.name,
                        "deals": len([d for d in deals if d.stage_id == stage.id]),
                        "value": sum(d.value or 0 for d in deals if d.stage_id == stage.id)
                    }
                    for stage in stages
                ]
            }
            
            # Use AI to analyze the pipeline
            pipeline_prompt = f"""
            Analyze this sales pipeline and provide insights:
            
            Pipeline Data: {json.dumps(pipeline_data, indent=2)}
            
            Provide:
            1. Pipeline health assessment
            2. Bottleneck identification
            3. Improvement recommendations
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a sales pipeline expert. Analyze pipeline data and provide strategic insights."},
                    {"role": "user", "content": pipeline_prompt}
                ],
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content and len(content) > 100:
                print("   ✅ Pipeline Analysis: PASS")
                print(f"   📝 Analysis length: {len(content)} characters")
            else:
                print("   ❌ Pipeline Analysis: FAIL")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Pipeline Analysis Test Failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all CRM integration tests"""
        print("🚀 CRM Integration Test Suite")
        print("=" * 50)
        
        tests = [
            ("CRM Data Access", self.test_crm_data_access),
            ("Email Personalization", self.test_email_personalization),
            ("Pipeline Analysis", self.test_pipeline_analysis)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {str(e)}")
        
        print(f"\n📊 CRM Integration Test Results:")
        print(f"  Passed: {passed}/{total}")
        print(f"  Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL CRM INTEGRATION TESTS PASSED!")
            print("✅ AI integration with CRM data is working perfectly")
            return True
        else:
            print("⚠️ Some CRM integration tests failed")
            return False

async def main():
    """Main test function"""
    try:
        test_suite = CRMIntegrationTest()
        success = await test_suite.run_all_tests()
        return success
    except Exception as e:
        print(f"❌ CRM Integration Test Suite Failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
