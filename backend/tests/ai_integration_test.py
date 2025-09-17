"""
Comprehensive AI Integration Test Suite
Tests all aspects of the AI sales assistant integration
"""
import os
import asyncio
import json
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our AI components
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.base import AIModel, AIMessage
from ai.data_access import CRMDataAccess
from ai.sales_assistant_optimized import OptimizedSalesAssistant
from ai.prompts.sales_prompts import SalesPrompts

# Import models and services
from api.models import Base, User, Organization, Contact, Lead, Deal, Stage, EmailTemplate
from api.email_automation import email_automation_service

class AIIntegrationTestSuite:
    """Comprehensive test suite for AI integration"""
    
    def __init__(self):
        self.test_results = {}
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Setup test database and environment"""
        # Create test database
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        
        # Create session
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()
        
        # Create test data
        self.create_test_data()
        
        # Initialize AI provider
        self.ai_provider = OpenAIProvider(model=AIModel.GPT_4O_MINI)
        
        print("✅ Test environment setup complete")
    
    def create_test_data(self):
        """Create comprehensive test data"""
        # Create test organization
        self.test_org = Organization(
            id=1,
            name="Test Company",
            domain="testcompany.com",
            settings='{"ai_enabled": true}'
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
            Stage(id=4, name="Negotiation", order=4),
            Stage(id=5, name="Closed Won", order=5)
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
                score=85,
                score_confidence=0.9,
                score_factors='{"company_size": "large", "budget": "high", "timeline": "urgent"}'
            ),
            Lead(
                id=2,
                title="TechStart - CRM Integration",
                contact_id=2,
                owner_id=1,
                organization_id=1,
                status="new",
                source="referral",
                score=65,
                score_confidence=0.7,
                score_factors='{"company_size": "medium", "budget": "medium", "timeline": "moderate"}'
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
                contact_id=1,
                description="Enterprise software license for 500 users"
            ),
            Deal(
                id=2,
                title="TechStart - Basic Package",
                value=5000.0,
                owner_id=1,
                stage_id=2,
                organization_id=1,
                contact_id=2,
                description="Basic CRM package for startup"
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
            ),
            EmailTemplate(
                id=2,
                name="Follow-up Email",
                category="follow_up",
                subject="Following up on {{lead.title}}",
                body="<p>Hi {{contact.name}},</p><p>I wanted to follow up on {{lead.title}}.</p>",
                created_by=1
            )
        ]
        for template in self.test_templates:
            self.db.add(template)
        
        self.db.commit()
        print("✅ Test data created successfully")
    
    async def run_all_tests(self):
        """Run all AI integration tests"""
        print("\n🚀 Starting Comprehensive AI Integration Tests\n")
        
        # Test 1: AI Provider Tests
        await self.test_ai_provider()
        
        # Test 2: Data Access Layer Tests
        await self.test_data_access_layer()
        
        # Test 3: Sales Assistant Tests
        await self.test_sales_assistant()
        
        # Test 4: Email Integration Tests
        await self.test_email_integration()
        
        # Test 5: Function Calling Tests
        await self.test_function_calling()
        
        # Test 6: Prompt Optimization Tests
        await self.test_prompt_optimization()
        
        # Test 7: Performance Tests
        await self.test_performance()
        
        # Test 8: Error Handling Tests
        await self.test_error_handling()
        
        # Generate test report
        self.generate_test_report()
    
    async def test_ai_provider(self):
        """Test AI provider functionality"""
        print("🧪 Testing AI Provider...")
        
        try:
            # Test basic chat completion
            messages = [
                AIMessage(role="system", content="You are a helpful assistant."),
                AIMessage(role="user", content="Say 'Hello, AI integration test!'")
            ]
            
            response = await self.ai_provider.chat_completion(messages=messages)
            
            assert response.content is not None
            assert len(response.content) > 0
            assert response.model == AIModel.GPT_4O_MINI.value
            
            self.test_results["ai_provider_basic"] = "✅ PASS"
            print("  ✅ Basic chat completion works")
            
            # Test entity extraction
            test_text = "John Smith from ACME Corp is interested in our enterprise software. His email is john@acmecorp.com and phone is 555-0123."
            schema = {
                "contact_name": "string",
                "company": "string", 
                "email": "string",
                "phone": "string",
                "interest": "string"
            }
            
            extracted = await self.ai_provider.extract_entities(test_text, schema)
            
            assert "contact_name" in extracted
            assert "company" in extracted
            assert extracted["contact_name"] == "John Smith"
            assert extracted["company"] == "ACME Corp"
            
            self.test_results["ai_provider_extraction"] = "✅ PASS"
            print("  ✅ Entity extraction works")
            
            # Test email generation
            template = "Hi {{contact.name}}, thank you for your interest in {{lead.title}}."
            context = {
                "contact": {"name": "John Smith"},
                "lead": {"title": "Enterprise Software"}
            }
            
            email = await self.ai_provider.generate_email(template, context)
            
            assert "John Smith" in email
            assert "Enterprise Software" in email
            
            self.test_results["ai_provider_email"] = "✅ PASS"
            print("  ✅ Email generation works")
            
            # Test sentiment analysis
            sentiment = await self.ai_provider.analyze_sentiment("I'm very interested in your product!")
            
            assert "sentiment" in sentiment
            assert sentiment["sentiment"] == "positive"
            
            self.test_results["ai_provider_sentiment"] = "✅ PASS"
            print("  ✅ Sentiment analysis works")
            
        except Exception as e:
            self.test_results["ai_provider"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ AI Provider test failed: {str(e)}")
    
    async def test_data_access_layer(self):
        """Test data access layer functionality"""
        print("🧪 Testing Data Access Layer...")
        
        try:
            data_access = CRMDataAccess(self.db, 1, 1)
            
            # Test user context
            user_context = data_access.get_user_context()
            
            assert "user" in user_context
            assert user_context["user"]["name"] == "Test Sales Rep"
            assert "performance" in user_context
            
            self.test_results["data_access_user"] = "✅ PASS"
            print("  ✅ User context retrieval works")
            
            # Test organization context
            org_context = data_access.get_organization_context()
            
            assert "organization" in org_context
            assert org_context["organization"]["name"] == "Test Company"
            assert "metrics" in org_context
            
            self.test_results["data_access_org"] = "✅ PASS"
            print("  ✅ Organization context retrieval works")
            
            # Test lead context
            lead_context = data_access.get_lead_context(1)
            
            assert "lead" in lead_context
            assert lead_context["lead"]["title"] == "ACME Corp - Enterprise Software"
            assert "contact" in lead_context
            assert lead_context["contact"]["name"] == "John Smith"
            
            self.test_results["data_access_lead"] = "✅ PASS"
            print("  ✅ Lead context retrieval works")
            
            # Test deal context
            deal_context = data_access.get_deal_context(1)
            
            assert "deal" in deal_context
            assert deal_context["deal"]["value"] == 50000.0
            assert "stage" in deal_context
            assert deal_context["stage"]["name"] == "Proposal"
            
            self.test_results["data_access_deal"] = "✅ PASS"
            print("  ✅ Deal context retrieval works")
            
            # Test contact context
            contact_context = data_access.get_contact_context(1)
            
            assert "contact" in contact_context
            assert contact_context["contact"]["name"] == "John Smith"
            assert "interaction_summary" in contact_context
            
            self.test_results["data_access_contact"] = "✅ PASS"
            print("  ✅ Contact context retrieval works")
            
            # Test pipeline summary
            pipeline = data_access.get_pipeline_summary()
            
            assert "stages" in pipeline
            assert len(pipeline["stages"]) == 5
            
            self.test_results["data_access_pipeline"] = "✅ PASS"
            print("  ✅ Pipeline summary works")
            
            # Test search functionality
            search_results = data_access.search_entities("ACME", ["contacts", "leads", "deals"])
            
            assert "contacts" in search_results
            assert "leads" in search_results
            assert "deals" in search_results
            assert len(search_results["contacts"]) > 0
            
            self.test_results["data_access_search"] = "✅ PASS"
            print("  ✅ Search functionality works")
            
        except Exception as e:
            self.test_results["data_access"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Data Access test failed: {str(e)}")
    
    async def test_sales_assistant(self):
        """Test sales assistant functionality"""
        print("🧪 Testing Sales Assistant...")
        
        try:
            assistant = OptimizedSalesAssistant(
                db=self.db,
                user_id=1,
                organization_id=1,
                provider=self.ai_provider
            )
            
            # Test basic message processing
            result = await assistant.process_message("What's my pipeline looking like?")
            
            assert "response" in result
            assert len(result["response"]) > 0
            assert "model" in result
            assert "timestamp" in result
            
            self.test_results["sales_assistant_basic"] = "✅ PASS"
            print("  ✅ Basic message processing works")
            
            # Test insights generation
            insights = await assistant.generate_sales_insights()
            
            assert "insights" in insights
            assert "performance_metrics" in insights
            assert "pipeline_summary" in insights
            
            self.test_results["sales_assistant_insights"] = "✅ PASS"
            print("  ✅ Sales insights generation works")
            
            # Test next actions suggestion
            actions = await assistant.suggest_next_actions("lead", 1)
            
            assert "suggestions" in actions
            assert "entity_context" in actions
            assert len(actions["suggestions"]) > 0
            
            self.test_results["sales_assistant_actions"] = "✅ PASS"
            print("  ✅ Next actions suggestion works")
            
        except Exception as e:
            self.test_results["sales_assistant"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Sales Assistant test failed: {str(e)}")
    
    async def test_email_integration(self):
        """Test email automation integration"""
        print("🧪 Testing Email Integration...")
        
        try:
            # Test email template personalization
            template = self.test_templates[0]
            context = {
                "contact": {"name": "John Smith", "company": "ACME Corp"},
                "user": {"name": "Test Sales Rep"}
            }
            
            personalized = email_automation_service.personalize_template(template, context)
            
            assert "John Smith" in personalized["subject"]
            assert "ACME Corp" in personalized["subject"]
            assert "John Smith" in personalized["body"]
            
            self.test_results["email_personalization"] = "✅ PASS"
            print("  ✅ Email personalization works")
            
            # Test template validation
            validation = email_automation_service.validate_template(template.body)
            
            assert "valid" in validation
            assert "available_variables" in validation
            
            self.test_results["email_validation"] = "✅ PASS"
            print("  ✅ Email template validation works")
            
            # Test context generation
            lead_context = email_automation_service.get_context_for_lead(self.test_leads[0], self.db)
            
            assert "lead" in lead_context
            assert "contact" in lead_context
            assert "user" in lead_context
            
            self.test_results["email_context"] = "✅ PASS"
            print("  ✅ Email context generation works")
            
        except Exception as e:
            self.test_results["email_integration"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Email Integration test failed: {str(e)}")
    
    async def test_function_calling(self):
        """Test function calling capabilities"""
        print("🧪 Testing Function Calling...")
        
        try:
            assistant = OptimizedSalesAssistant(
                db=self.db,
                user_id=1,
                organization_id=1,
                provider=self.ai_provider
            )
            
            # Test get_lead_details function
            function_call = {
                "name": "get_lead_details",
                "arguments": {"lead_id": 1}
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == True
            assert "lead" in result["result"]
            assert result["result"]["lead"]["title"] == "ACME Corp - Enterprise Software"
            
            self.test_results["function_lead_details"] = "✅ PASS"
            print("  ✅ Lead details function works")
            
            # Test get_deal_details function
            function_call = {
                "name": "get_deal_details",
                "arguments": {"deal_id": 1}
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == True
            assert "deal" in result["result"]
            assert result["result"]["deal"]["value"] == 50000.0
            
            self.test_results["function_deal_details"] = "✅ PASS"
            print("  ✅ Deal details function works")
            
            # Test search_crm function
            function_call = {
                "name": "search_crm",
                "arguments": {"query": "ACME", "entity_types": ["contacts", "leads"]}
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == True
            assert "contacts" in result["result"]
            assert "leads" in result["result"]
            
            self.test_results["function_search"] = "✅ PASS"
            print("  ✅ Search function works")
            
            # Test generate_email function
            function_call = {
                "name": "generate_email",
                "arguments": {
                    "template_id": 1,
                    "recipient_id": 1,
                    "recipient_type": "contact"
                }
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == True
            assert "subject" in result["result"]
            assert "body" in result["result"]
            
            self.test_results["function_email"] = "✅ PASS"
            print("  ✅ Email generation function works")
            
        except Exception as e:
            self.test_results["function_calling"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Function Calling test failed: {str(e)}")
    
    async def test_prompt_optimization(self):
        """Test prompt optimization and specialized prompts"""
        print("🧪 Testing Prompt Optimization...")
        
        try:
            # Test system prompt generation
            system_prompt = SalesPrompts.get_system_prompt("Test Company", "Test Sales Rep", "sales_rep")
            
            assert "Test Company" in system_prompt
            assert "Test Sales Rep" in system_prompt
            assert "sales_rep" in system_prompt
            assert "Data-Driven" in system_prompt
            
            self.test_results["prompt_system"] = "✅ PASS"
            print("  ✅ System prompt generation works")
            
            # Test lead qualification prompt
            lead_prompt = SalesPrompts.get_lead_qualification_prompt()
            
            assert "Lead Score Analysis" in lead_prompt
            assert "Qualification Status" in lead_prompt
            assert "Buying Signals" in lead_prompt
            
            self.test_results["prompt_lead_qualification"] = "✅ PASS"
            print("  ✅ Lead qualification prompt works")
            
            # Test deal strategy prompt
            deal_prompt = SalesPrompts.get_deal_strategy_prompt()
            
            assert "Current Status" in deal_prompt
            assert "Key Stakeholders" in deal_prompt
            assert "Closing Strategy" in deal_prompt
            
            self.test_results["prompt_deal_strategy"] = "✅ PASS"
            print("  ✅ Deal strategy prompt works")
            
            # Test email personalization prompt
            email_prompt = SalesPrompts.get_email_personalization_prompt()
            
            assert "Tone Matching" in email_prompt
            assert "Context Awareness" in email_prompt
            assert "Call-to-Action" in email_prompt
            
            self.test_results["prompt_email_personalization"] = "✅ PASS"
            print("  ✅ Email personalization prompt works")
            
        except Exception as e:
            self.test_results["prompt_optimization"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Prompt Optimization test failed: {str(e)}")
    
    async def test_performance(self):
        """Test performance and optimization"""
        print("🧪 Testing Performance...")
        
        try:
            assistant = OptimizedSalesAssistant(
                db=self.db,
                user_id=1,
                organization_id=1,
                provider=self.ai_provider
            )
            
            # Test response time
            start_time = datetime.now()
            result = await assistant.process_message("Give me a quick summary of my leads")
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            assert response_time < 10.0  # Should respond within 10 seconds
            assert "response" in result
            
            self.test_results["performance_response_time"] = f"✅ PASS ({response_time:.2f}s)"
            print(f"  ✅ Response time: {response_time:.2f} seconds")
            
            # Test model info
            model_info = self.ai_provider.get_model_info()
            
            assert "provider" in model_info
            assert "model" in model_info
            assert "supports_functions" in model_info
            assert model_info["supports_functions"] == True
            
            self.test_results["performance_model_info"] = "✅ PASS"
            print("  ✅ Model info retrieval works")
            
            # Test cost information
            cost_info = self.ai_provider._get_cost_info()
            
            assert "input" in cost_info
            assert "output" in cost_info
            assert cost_info["input"] > 0
            assert cost_info["output"] > 0
            
            self.test_results["performance_cost_info"] = "✅ PASS"
            print("  ✅ Cost information works")
            
        except Exception as e:
            self.test_results["performance"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Performance test failed: {str(e)}")
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🧪 Testing Error Handling...")
        
        try:
            assistant = OptimizedSalesAssistant(
                db=self.db,
                user_id=1,
                organization_id=1,
                provider=self.ai_provider
            )
            
            # Test invalid function call
            function_call = {
                "name": "invalid_function",
                "arguments": {}
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == False
            assert "error" in result
            
            self.test_results["error_invalid_function"] = "✅ PASS"
            print("  ✅ Invalid function handling works")
            
            # Test invalid entity ID
            function_call = {
                "name": "get_lead_details",
                "arguments": {"lead_id": 99999}
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == True  # Should return empty result, not error
            assert result["result"] == {}
            
            self.test_results["error_invalid_id"] = "✅ PASS"
            print("  ✅ Invalid ID handling works")
            
            # Test malformed function arguments
            function_call = {
                "name": "generate_email",
                "arguments": {"template_id": "invalid"}  # Should be integer
            }
            
            result = await assistant._execute_function(function_call)
            
            assert result["success"] == False
            assert "error" in result
            
            self.test_results["error_malformed_args"] = "✅ PASS"
            print("  ✅ Malformed arguments handling works")
            
        except Exception as e:
            self.test_results["error_handling"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Error Handling test failed: {str(e)}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 AI INTEGRATION TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.startswith("✅")])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 SUMMARY:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            print(f"  {test_name}: {result}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! AI integration is working perfectly.")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Review the errors above.")
        
        print("\n" + "="*60)
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open("ai_integration_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("📄 Test report saved to: ai_integration_test_report.json")

# Main test runner
async def run_ai_integration_tests():
    """Run the complete AI integration test suite"""
    test_suite = AIIntegrationTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(run_ai_integration_tests())
