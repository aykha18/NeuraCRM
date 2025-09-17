#!/usr/bin/env python3
"""
API Endpoint Test
Tests the enhanced AI API endpoints
"""
import asyncio
import json
import requests
from datetime import datetime

class APIEndpointTest:
    """Test API endpoints"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
    
    def test_health_check(self):
        """Test basic health check"""
        print("🧪 Testing Health Check...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("   ✅ Health Check: PASS")
                return True
            else:
                print(f"   ❌ Health Check: FAIL - Status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Health Check: FAIL - {str(e)}")
            return False
    
    def test_ai_enhanced_chat(self):
        """Test enhanced AI chat endpoint"""
        print("🧪 Testing Enhanced AI Chat...")
        
        try:
            # Test basic chat
            data = {
                "message": "Hello, can you help me with my sales pipeline?",
                "include_insights": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai-enhanced/chat",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "response" in result and "model" in result:
                    print("   ✅ Enhanced AI Chat: PASS")
                    print(f"   📝 Response length: {len(result['response'])} characters")
                    return True
                else:
                    print("   ❌ Enhanced AI Chat: FAIL - Invalid response format")
                    return False
            else:
                print(f"   ❌ Enhanced AI Chat: FAIL - Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Enhanced AI Chat: FAIL - {str(e)}")
            return False
    
    def test_sales_insights(self):
        """Test sales insights endpoint"""
        print("🧪 Testing Sales Insights...")
        
        try:
            data = {}
            
            response = requests.post(
                f"{self.base_url}/api/ai-enhanced/insights",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "insights" in result:
                    print("   ✅ Sales Insights: PASS")
                    return True
                else:
                    print("   ❌ Sales Insights: FAIL - No insights in response")
                    return False
            else:
                print(f"   ❌ Sales Insights: FAIL - Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Sales Insights: FAIL - {str(e)}")
            return False
    
    def test_email_templates(self):
        """Test email templates endpoint"""
        print("🧪 Testing Email Templates...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/ai-enhanced/templates",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "templates" in result:
                    print("   ✅ Email Templates: PASS")
                    return True
                else:
                    print("   ❌ Email Templates: FAIL - No templates in response")
                    return False
            else:
                print(f"   ❌ Email Templates: FAIL - Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Email Templates: FAIL - {str(e)}")
            return False
    
    def test_model_info(self):
        """Test model info endpoint"""
        print("🧪 Testing Model Info...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/ai-enhanced/model-info",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "model_info" in result:
                    print("   ✅ Model Info: PASS")
                    return True
                else:
                    print("   ❌ Model Info: FAIL - No model_info in response")
                    return False
            else:
                print(f"   ❌ Model Info: FAIL - Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Model Info: FAIL - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API endpoint tests"""
        print("🚀 API Endpoint Test Suite")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Enhanced AI Chat", self.test_ai_enhanced_chat),
            ("Sales Insights", self.test_sales_insights),
            ("Email Templates", self.test_email_templates),
            ("Model Info", self.test_model_info)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {str(e)}")
        
        print(f"\n📊 API Endpoint Test Results:")
        print(f"  Passed: {passed}/{total}")
        print(f"  Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL API ENDPOINT TESTS PASSED!")
            return True
        else:
            print("⚠️ Some API endpoint tests failed")
            return False

def main():
    """Main test function"""
    test_suite = APIEndpointTest()
    success = test_suite.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
