"""
API Endpoint Testing Suite
Tests all enhanced AI API endpoints with real requests
"""
import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, Any

class APIEndpointTestSuite:
    """Test suite for AI API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.auth_token = None
    
    async def run_all_tests(self):
        """Run all API endpoint tests"""
        print("\n🚀 Starting API Endpoint Tests\n")
        
        # Setup authentication
        await self.setup_auth()
        
        # Test 1: Enhanced Chat Endpoint
        await self.test_enhanced_chat()
        
        # Test 2: Sales Insights Endpoint
        await self.test_sales_insights()
        
        # Test 3: Email Generation Endpoint
        await self.test_email_generation()
        
        # Test 4: CRM Search Endpoint
        await self.test_crm_search()
        
        # Test 5: Pipeline Analysis Endpoint
        await self.test_pipeline_analysis()
        
        # Test 6: Email Templates Endpoint
        await self.test_email_templates()
        
        # Test 7: Model Info Endpoint
        await self.test_model_info()
        
        # Generate API test report
        self.generate_api_test_report()
    
    async def setup_auth(self):
        """Setup authentication for API tests"""
        print("🔐 Setting up authentication...")
        
        # For testing, we'll use a mock token
        # In real implementation, you'd authenticate properly
        self.auth_token = "test_token_123"
        
        print("✅ Authentication setup complete")
    
    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "response_time": response.elapsed.total_seconds()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def test_enhanced_chat(self):
        """Test enhanced chat endpoint"""
        print("🧪 Testing Enhanced Chat Endpoint...")
        
        test_cases = [
            {
                "name": "Basic Chat",
                "data": {
                    "message": "Hello, can you help me with my sales pipeline?",
                    "include_insights": False
                }
            },
            {
                "name": "Chat with Insights",
                "data": {
                    "message": "Analyze my current deals and suggest improvements",
                    "include_insights": True
                }
            },
            {
                "name": "Chat with History",
                "data": {
                    "message": "What's the status of my ACME Corp deal?",
                    "conversation_history": [
                        {"role": "user", "content": "Show me my deals"},
                        {"role": "assistant", "content": "Here are your current deals..."}
                    ],
                    "include_insights": False
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.make_request("POST", "/api/ai-enhanced/chat", test_case["data"])
                
                if result["success"]:
                    assert "response" in result["data"]
                    assert "model" in result["data"]
                    assert "timestamp" in result["data"]
                    
                    if test_case["data"].get("include_insights"):
                        assert "insights" in result["data"]
                    
                    self.test_results[f"chat_{test_case['name'].lower().replace(' ', '_')}"] = f"✅ PASS ({result['response_time']:.2f}s)"
                    print(f"  ✅ {test_case['name']}: {result['response_time']:.2f}s")
                else:
                    self.test_results[f"chat_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {result['error']}"
                    print(f"  ❌ {test_case['name']}: {result['error']}")
                    
            except Exception as e:
                self.test_results[f"chat_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {str(e)}"
                print(f"  ❌ {test_case['name']}: {str(e)}")
    
    async def test_sales_insights(self):
        """Test sales insights endpoint"""
        print("🧪 Testing Sales Insights Endpoint...")
        
        test_cases = [
            {
                "name": "General Insights",
                "data": {}
            },
            {
                "name": "Lead Insights",
                "data": {
                    "entity_type": "lead",
                    "entity_id": 1
                }
            },
            {
                "name": "Deal Insights",
                "data": {
                    "entity_type": "deal",
                    "entity_id": 1
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.make_request("POST", "/api/ai-enhanced/insights", test_case["data"])
                
                if result["success"]:
                    assert "insights" in result["data"]
                    assert "generated_at" in result["data"]
                    
                    self.test_results[f"insights_{test_case['name'].lower().replace(' ', '_')}"] = f"✅ PASS ({result['response_time']:.2f}s)"
                    print(f"  ✅ {test_case['name']}: {result['response_time']:.2f}s")
                else:
                    self.test_results[f"insights_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {result['error']}"
                    print(f"  ❌ {test_case['name']}: {result['error']}")
                    
            except Exception as e:
                self.test_results[f"insights_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {str(e)}"
                print(f"  ❌ {test_case['name']}: {str(e)}")
    
    async def test_email_generation(self):
        """Test email generation endpoint"""
        print("🧪 Testing Email Generation Endpoint...")
        
        test_cases = [
            {
                "name": "Contact Email",
                "data": {
                    "template_id": 1,
                    "recipient_id": 1,
                    "recipient_type": "contact",
                    "send_immediately": False
                }
            },
            {
                "name": "Lead Email with Custom Context",
                "data": {
                    "template_id": 2,
                    "recipient_id": 1,
                    "recipient_type": "lead",
                    "custom_context": {
                        "urgency": "high",
                        "special_offer": "20% discount"
                    },
                    "send_immediately": False
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.make_request("POST", "/api/ai-enhanced/generate-email", test_case["data"])
                
                if result["success"]:
                    assert "email" in result["data"]
                    assert "subject" in result["data"]["email"]
                    assert "body" in result["data"]["email"]
                    assert "recipient" in result["data"]["email"]
                    
                    self.test_results[f"email_{test_case['name'].lower().replace(' ', '_')}"] = f"✅ PASS ({result['response_time']:.2f}s)"
                    print(f"  ✅ {test_case['name']}: {result['response_time']:.2f}s")
                else:
                    self.test_results[f"email_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {result['error']}"
                    print(f"  ❌ {test_case['name']}: {result['error']}")
                    
            except Exception as e:
                self.test_results[f"email_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {str(e)}"
                print(f"  ❌ {test_case['name']}: {str(e)}")
    
    async def test_crm_search(self):
        """Test CRM search endpoint"""
        print("🧪 Testing CRM Search Endpoint...")
        
        test_cases = [
            {
                "name": "Search All Entities",
                "data": {
                    "query": "ACME",
                    "entity_types": ["contacts", "leads", "deals"]
                }
            },
            {
                "name": "Search Contacts Only",
                "data": {
                    "query": "John",
                    "entity_types": ["contacts"]
                }
            },
            {
                "name": "Search with Special Characters",
                "data": {
                    "query": "TechStart Inc",
                    "entity_types": ["contacts", "leads"]
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.make_request("POST", "/api/ai-enhanced/search", test_case["data"])
                
                if result["success"]:
                    assert "results" in result["data"]
                    assert "insights" in result["data"]
                    assert "total_results" in result["data"]
                    
                    self.test_results[f"search_{test_case['name'].lower().replace(' ', '_')}"] = f"✅ PASS ({result['response_time']:.2f}s)"
                    print(f"  ✅ {test_case['name']}: {result['response_time']:.2f}s")
                else:
                    self.test_results[f"search_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {result['error']}"
                    print(f"  ❌ {test_case['name']}: {result['error']}")
                    
            except Exception as e:
                self.test_results[f"search_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {str(e)}"
                print(f"  ❌ {test_case['name']}: {str(e)}")
    
    async def test_pipeline_analysis(self):
        """Test pipeline analysis endpoint"""
        print("🧪 Testing Pipeline Analysis Endpoint...")
        
        try:
            result = self.make_request("GET", "/api/ai-enhanced/pipeline-analysis")
            
            if result["success"]:
                assert "pipeline_data" in result["data"]
                assert "ai_analysis" in result["data"]
                assert "generated_at" in result["data"]
                
                self.test_results["pipeline_analysis"] = f"✅ PASS ({result['response_time']:.2f}s)"
                print(f"  ✅ Pipeline Analysis: {result['response_time']:.2f}s")
            else:
                self.test_results["pipeline_analysis"] = f"❌ FAIL: {result['error']}"
                print(f"  ❌ Pipeline Analysis: {result['error']}")
                
        except Exception as e:
            self.test_results["pipeline_analysis"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Pipeline Analysis: {str(e)}")
    
    async def test_email_templates(self):
        """Test email templates endpoint"""
        print("🧪 Testing Email Templates Endpoint...")
        
        test_cases = [
            {
                "name": "All Templates",
                "endpoint": "/api/ai-enhanced/templates"
            },
            {
                "name": "Welcome Templates",
                "endpoint": "/api/ai-enhanced/templates?category=welcome"
            },
            {
                "name": "Follow-up Templates",
                "endpoint": "/api/ai-enhanced/templates?category=follow_up"
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.make_request("GET", test_case["endpoint"])
                
                if result["success"]:
                    assert "templates" in result["data"]
                    assert "total" in result["data"]
                    
                    self.test_results[f"templates_{test_case['name'].lower().replace(' ', '_')}"] = f"✅ PASS ({result['response_time']:.2f}s)"
                    print(f"  ✅ {test_case['name']}: {result['response_time']:.2f}s")
                else:
                    self.test_results[f"templates_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {result['error']}"
                    print(f"  ❌ {test_case['name']}: {result['error']}")
                    
            except Exception as e:
                self.test_results[f"templates_{test_case['name'].lower().replace(' ', '_')}"] = f"❌ FAIL: {str(e)}"
                print(f"  ❌ {test_case['name']}: {str(e)}")
    
    async def test_model_info(self):
        """Test model info endpoint"""
        print("🧪 Testing Model Info Endpoint...")
        
        try:
            result = self.make_request("GET", "/api/ai-enhanced/model-info")
            
            if result["success"]:
                assert "model_info" in result["data"]
                assert "provider" in result["data"]["model_info"]
                assert "model" in result["data"]["model_info"]
                assert "supports_functions" in result["data"]["model_info"]
                
                self.test_results["model_info"] = f"✅ PASS ({result['response_time']:.2f}s)"
                print(f"  ✅ Model Info: {result['response_time']:.2f}s")
            else:
                self.test_results["model_info"] = f"❌ FAIL: {result['error']}"
                print(f"  ❌ Model Info: {result['error']}")
                
        except Exception as e:
            self.test_results["model_info"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Model Info: {str(e)}")
    
    def generate_api_test_report(self):
        """Generate API test report"""
        print("\n" + "="*60)
        print("📊 API ENDPOINT TEST REPORT")
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
            print(f"\n🎉 ALL API TESTS PASSED! All endpoints are working correctly.")
        else:
            print(f"\n⚠️  {failed_tests} API tests failed. Review the errors above.")
        
        print("\n" + "="*60)
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open("api_endpoint_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("📄 API test report saved to: api_endpoint_test_report.json")

# Main test runner
async def run_api_endpoint_tests():
    """Run the complete API endpoint test suite"""
    test_suite = APIEndpointTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(run_api_endpoint_tests())
